import io
import math
import os
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pyzed.sl as sl
import setproctitle

sys.path.append('./')

from base.message import ImageLink, Sensor, SensorZ
from base.network import Net
from base.timer import Timer

from PIL import Image

#####################
# CONFIG PARAMETERS #
FPS = 10
#####################

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


def send_img(image, port):
    des_res = (480, 270)
    arr = image.get_data()
    b, g, r, _ = [np.asarray(arr[:, :, layer], dtype='uint8') for layer in range(4)]

    raw_img = np.dstack((b, g, r))
    raw_img = cv2.resize(raw_img, des_res)

    is_success, jpg_buff = cv2.imencode('.jpg', raw_img)

    if sys.getsizeof(jpg_buff) > 65535:
        ratio = 65535 / sys.getsizeof(jpg_buff)
        raw_img = cv2.resize(raw_img, (math.floor(des_res[0] * ratio), math.floor(des_res[1] * ratio)))
        is_success, jpg_buff = cv2.imencode('.jpg', raw_img)
        print(f'extra compressed:{(math.floor(des_res[0] * ratio), math.floor(des_res[1] * ratio))}')

    sock_set.sendto(jpg_buff.tobytes(), ("255.255.255.255", port))


def main(name: str, serial: np.uint32, is_stream: bool = False, pose_tracking: bool = False) -> None:
    net = Net(1 / FPS)
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
    init_params.camera_image_flip = sl.FLIP_MODE.OFF

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
                save_path = PATH_PREFIX + "/" + name + "/" + datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
                if not os.path.exists(save_path):
                    Path(save_path).mkdir(parents=True, exist_ok=True)

        if net.id == "PhotoOff":
            if net.msg.camera == name:
                img_capture = False

        if net.id == "Timer":
            time1 = time.time()
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

                file = f"{photo_counter:05d}.png"
                path = f"{save_path}/{file}"

                arr = image.get_data()
                b, g, r, _ = Image.fromarray(arr).split()
                png = Image.merge('RGB', (r, g, b))

                png = png.resize((456, 256))
                png = png.crop((100, 0, 356, 256))

                if name == 'Bottom':
                    png = png.rotate(-90)

                png.save(fp=path)
                net.send(ImageLink(
                    obj=name,
                    path=path,
                    file=file,
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
                    pos_pitch=z.item(), pos_roll=y - ROLL_OFFSET,
                    vel_pitch=vz.item(), vel_roll=-vx.item(),
                ))
                net.send(SensorZ(
                    pos_yaw=-x.item(),
                    vel_yaw=vy.item(),
                ))

            time2 = time.time()
            if is_stream:
                if name == 'Front':
                    send_img(image, PORT_FRONT)
                elif name == 'Bottom':
                    send_img(image, PORT_BOTTOM)

                if time2 - time1 > 0.05:
                    print(f'Camera iteration slow: {time2 - time1}')
            else:
                if time2 - time1 > 0.25:
                    print(f'Camera iteration slow: {time2 - time1}')

    print(f'[{name}] Close the camera')
    zed.close()


if __name__ == "__main__":
    name = sys.argv[1]
    serial = int(sys.argv[2])
    pose_tracking = sys.argv[3] == "True"
    is_stream = len(sys.argv) == 5 and sys.argv[4] == "True"

    main(name=name, serial=serial, is_stream=is_stream, pose_tracking=pose_tracking)
