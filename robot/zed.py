import sys

import pyzed.sl as sl
import numpy as np
import time
import setproctitle

sys.path.append('..')

from base.network import Net
from base.message import Sensor, ImageLink

setproctitle.setproctitle(' '.join(sys.argv))


class Timer:
    def __init__(self, delay_sec: float):
        self.delay_sec = delay_sec
        self.next = time.time() + delay_sec

    @property
    def is_unlock(self):
        unlock = self.next < time.time()
        if unlock:
            self.next = time.time() + self.delay_sec
        return unlock


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


def main(name: str, serial: np.uint32, is_stream: bool = False, pose_tracking: bool = False) -> None:
    net = Net(1)
    send_timer = Timer(0.1)

    img_capture = False
    save_path = ''

    print(f'[{name}] Configure init parameters')
    init_params = sl.InitParameters()
    init_params.set_from_serial_number(serial)
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
    init_params.coordinate_units = sl.UNIT.METER
    init_params.depth_mode = sl.DEPTH_MODE.NONE
    init_params.camera_fps = 10

    print(f'[{name}] Open the camera')
    zed = sl.Camera()
    zed_status = zed.open(init_params)
    if zed_status != sl.ERROR_CODE.SUCCESS:
        print(f'[{name}] {repr(zed_status)}')
        exit(1)

    print(f'[{name}] Configure runtime parameters')
    runtime_params = sl.RuntimeParameters()

    if is_stream:
        print(f'[{name}] Configuring stream parameters')
        stream_params = sl.StreamingParameters()
        stream_params.codec = sl.STREAMING_CODEC.H264
        stream_params.bitrate = 4000
        stream_params.port = 30000

        zed_status = zed.enable_streaming(stream_params)
        if zed_status != sl.ERROR_CODE.SUCCESS:
            print(repr(zed_status))
            exit(1)

    print(f'[{name}] Init sensors data')
    sensors_data = sl.SensorsData()

    image = sl.Mat()

    while net.receive():
        zed_status = zed.grab(runtime_params)
        if zed_status != sl.ERROR_CODE.SUCCESS:
            print(f'[{name}] {repr(zed_status)}')
            continue

        if net.id == "PhotoSave":
            img_capture = True
            save_path = net.msg.folder

        if net.id == "Timer" and img_capture:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            timestamp = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE)
            path = f"{save_path}/{timestamp}.jpg"

            image.write(path)
            net.send(ImageLink(
                obj=name,
                path=path
            ))

        if send_timer.is_unlock and pose_tracking:
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
                pos_yaw=-x.item(), pos_pitch=z.item(), pos_roll=-y,
                vel_yaw=-vx.item(), vel_pitch=vz.item(), vel_roll=-vy.item(),
            ))

    if is_stream:
        print(f'[{name}] Disable streaming')
        zed.disable_streaming()

    print(f'[{name}] Close the camera')
    zed.close()


if __name__ == "__main__":
    name = sys.argv[1]
    serial = int(sys.argv[2])
    pose_tracking = sys.argv[3] == "True"
    is_stream = len(sys.argv) == 5 and sys.argv[4] == "True"

    main(name=name, serial=serial, is_stream=is_stream, pose_tracking=pose_tracking)
