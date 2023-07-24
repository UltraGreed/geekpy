import datetime
import io
import math
import os
import socket
import sys
import time

import numpy as np
import pyzed.sl as sl
import setproctitle
from PIL import Image

sys.path.append('./')

from base.message import ImageLink, Sensor
from base.network import Net
from base.timer import Timer

setproctitle.setproctitle(' '.join(sys.argv))

PATH_PREFIX = '/media/ssd/photo'
ROLL_OFFSET = 3.3

sock_set = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

PORT_FRONT = 1111
PORT_BOTTOM = 1112


def quat2eul(qx, qy, qz, qw) -> np.array:
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = np.arctan2(sinr_cosp, cosr_cosp)  # x

    sinp = 1 + 2 * (qw * qy - qx * qz)
    cosp = 1 - 2 * (qw * qy - qx * qz)
    pitch = 2 * np.arctan2(sinp, cosp) - np.pi / 2  # y

    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw = np.arctan2(siny_cosp, cosy_cosp)  # z

    return np.rad2deg((yaw, roll, pitch))


def jpgByteArray(image):
    imageBytesIO = io.BytesIO()
    image.save(imageBytesIO, format="JPEG")
    return imageBytesIO.getvalue()


def send_img(image, port):
    arr = image.get_data()
    b, g, r, _ = Image.fromarray(arr).split()
    png = Image.merge('RGB', (r, g, b))

    jpg = jpgByteArray(png.resize((910, 512)))

    if sys.getsizeof(jpg) > 65535:
        ratio =  65535 / sys.getsizeof(jpg)
        jpg = jpgByteArray(png.resize((math.floor(910 * ratio), math.floor(512 * ratio))))

    sock_set.sendto(jpg, ("255.255.255.255", port))


def main(name: str, serial: np.uint32, is_stream: bool = False, pose_tracking: bool = False) -> None:
    net = Net(0.1)
    photo_timer = Timer(0.25)

    img_capture = False
    save_path = '/media/ssd/photo'

    print(f'[{name}] Configure init parameters')
    init_params = sl.InitParameters()
    init_params.set_from_serial_number(serial)
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
    init_params.coordinate_units = sl.UNIT.METER
    init_params.depth_mode = sl.DEPTH_MODE.NONE
    init_params.camera_fps = 30

    print(f'[{name}] Open the camera')
    zed = sl.Camera()
    zed_status = zed.open(init_params)
    while zed_status != sl.ERROR_CODE.SUCCESS:
        print(f'[{name}] {repr(zed_status)}')
        zed_status = zed.open(init_params)

    print(f'[{name}] Configure runtime parameters')
    runtime_params = sl.RuntimeParameters()

    print(f'[{name}] Init sensors data')
    sensors_data = sl.SensorsData()

    resolution = (1280, 720)
    image = sl.Mat(*resolution, sl.MAT_TYPE.U8_C1)

    photo_counter = 0

    while net.receive():
        if net.id == "PhotoOn":
            if net.msg.camera == name:
                img_capture = True
                save_path = PATH_PREFIX + "/" + net.msg.folder
                if not os.path.exists(save_path):
                    os.mkdir(save_path)

        if net.id == "PhotoOff":
            if net.msg.camera == name:
                img_capture = False

        if net.id == "Timer":
            zed_status = zed.grab(runtime_params)
            if zed_status != sl.ERROR_CODE.SUCCESS:
                print(f'[{name}] {repr(zed_status)}')
                continue

            if name == 'Front':
                zed.retrieve_image(image, sl.VIEW.LEFT)
            elif name == 'Bottom':
                zed.retrieve_image(image, sl.VIEW.RIGHT)

            if photo_timer.is_unlock and img_capture:
                photo_counter += 1

                timestamp = datetime.datetime.today().strftime("%Y%m%d_%H%M%S.%f")
                path = f"{save_path}/{name}_{timestamp}.jpg"

                arr = image.get_data()
                b, g, r, _ = Image.fromarray(arr).split()
                png = Image.merge('RGB', (r, g, b))

                png = png.resize((456, 256))
                png = png.crop((100, 0, 356, 256))
                png = png.rotate(-90)

                png.save(fp=path)
                net.send(ImageLink(
                    obj=name,
                    path=path,
                    file=f'{name}_{timestamp}.jpg',
                    counter=photo_counter
                ))

            if pose_tracking:
                zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)
                zed_imu = sensors_data.get_imu_data()

                # deg/sec
                a_velocity = zed_imu.get_angular_velocity()
                vx, vy, vz = np.round(a_velocity, 3)

                # m/sec^2
                # a_accel = zed_imu.get_linear_acceleration()
                # ax, ay, az = np.round(a_accel, 3)

                x, y, z = quat2eul(*zed_imu.get_pose().get_orientation().get())

                y = -y.item() - 90
                if y < -90:
                    y = -90
                if y > 90:
                    y = 90

                net.send(Sensor(
                    pos_yaw=-x.item(), pos_pitch=z.item(), pos_roll=y - ROLL_OFFSET,
                    vel_yaw=vy.item(), vel_pitch=vz.item(), vel_roll=-vx.item(),
                ))

            if is_stream:
                if name == 'Front':
                    send_img(image, PORT_FRONT)
                elif name == 'Bottom':
                    send_img(image, PORT_BOTTOM)

    print(f'[{name}] Close the camera')
    zed.close()


if __name__ == "__main__":
    name = sys.argv[1]
    serial = int(sys.argv[2])
    pose_tracking = sys.argv[3] == "True"
    is_stream = len(sys.argv) == 5 and sys.argv[4] == "True"

    main(name=name, serial=serial, is_stream=is_stream, pose_tracking=pose_tracking)
