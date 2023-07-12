import pyzed.sl as sl
import numpy as np
import time

from base.network import Net
from base.message import Sensor


class Timer:
    def __init__(self, delay_sec: float):
        self.delay_sec = delay_sec
        self.next = time.time() + delay_sec

    @property
    def is_unlock(self):
        unlock = time.time() > self.next
        if unlock:
            self.next = time.time() + self.delay_sec
        return unlock


def main(serial: np.uint32, img_capture: bool = False, is_stream: bool = False, pose_tracking: bool = False):
    net = Net()
    send_timer = Timer(0.1)

    print('Configure init parameters')
    init_params = sl.InitParameters()
    init_params.set_from_serial_number(serial)
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.coordinate_units = sl.UNIT.METER
    init_params.depth_mode = sl.DEPTH_MODE.NONE
    init_params.camera_fps = 10

    print('Open the camera')
    zed = sl.Camera()
    zed_status = zed.open(init_params)
    if zed_status != sl.ERROR_CODE.SUCCESS:
        print(repr(zed_status))
        exit(1)

    print('Configure runtime parameters')
    runtime_params = sl.RuntimeParameters()

    if is_stream:
        print('Configuring stream parameters')
        stream_params = sl.StreamingParameters()
        stream_params.codec = sl.STREAMING_CODEC.H264
        stream_params.bitrate = 4000
        stream_params.port = 30000

        zed_status = zed.enable_streaming(stream_params)
        if zed_status != sl.ERROR_CODE.SUCCESS:
            print(repr(zed_status))
            exit(1)

    print('Init sensors data')
    sensors_data = sl.SensorsData()

    image = sl.Mat()

    while net.receive():
        zed_status = zed.grab(runtime_params)
        if zed_status != sl.ERROR_CODE.SUCCESS:
            print(zed_status)
            continue

        if img_capture:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            image.write()

        if send_timer.is_unlock and pose_tracking:
            zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)
            zed_imu = sensors_data.get_imu_data()

            a_velocity = zed_imu.get_angular_velocity()
            vx, vy, vz = np.round(a_velocity, 3)

            a_accel = zed_imu.get_linear_acceleration()
            ax, ay, az = np.round(a_accel, 3)

            print(f"{vx=} {vy=} {vz=}")
            print(f"{ax=} {ay=} {az=}")
            print('-' * 50)

            net.send(Sensor(
                vel_x=vx, vel_y=vy, vel_depth=vz,
                acc_x=ax, acc_y=ay, acc_depth=az
            ))

    if is_stream:
        print('Disable streaming')
        zed.disable_streaming()

    print('Close the camera')
    zed.close()


if __name__ == "__main__":
    main(np.uint32(38934910), pose_tracking=True)
