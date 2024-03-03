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

sys.path.append("./")

from base.message import ImageLink, Sensor, SensorZ
from base.network import Net
from base.timer import Timer
from PIL import Image

import argparse  # IMP: argparse
import logging  # IMP: logging

setproctitle.setproctitle(" ".join(sys.argv))

SAVE_PATH = "/media/ssd/photo"
ROLL_OFFSET = 3.3

sock_set = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

PORT_FRONT = 1111
PORT_BOTTOM = 1112


class TimestampHandler:
    def __init__(self) -> None:
        self.ts = sl.Timestamp()

    def is_new(self, sensor) -> bool:
        new_ = sensor.timestamp.get_microseconds() > self.ts.get_microseconds()
        if new_:
            self.ts = sensor.timestamp

        return new_


def quat2eul(qx, qy, qz, qw) -> np.ndarray:
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
    b, g, r, _ = [np.asarray(arr[:, :, layer], dtype="uint8") for layer in range(4)]

    raw_img = np.dstack((b, g, r))
    raw_img = cv2.resize(raw_img, des_res)

    _, jpg_buff = cv2.imencode(".jpg", raw_img)

    if sys.getsizeof(jpg_buff) > 65535:
        ratio = 65535 / sys.getsizeof(jpg_buff)
        raw_img = cv2.resize(
            raw_img, (math.floor(des_res[0] * ratio), math.floor(des_res[1] * ratio))
        )
        _, jpg_buff = cv2.imencode(".jpg", raw_img)
        print(
            f"extra compressed:{(math.floor(des_res[0] * ratio), math.floor(des_res[1] * ratio))}"
        )

    sock_set.sendto(jpg_buff.tobytes(), ("255.255.255.255", port))


def img_cap():
    pass


def sensor_cap():
    pass


def main(
    *,
    name: str,
    serial: int,
    is_stream: bool = False,
    pose_tracking: bool = False,
    is_img_capture: bool = False,
    fps: int = 20,
    photo_capture_delay: float = 1 / 5,
) -> None:
    net = Net(1 / fps)
    photo_timer = Timer(photo_capture_delay)

    # REMOVE
    is_img_capture = True
    # END REMOVE

    print(f"[{name}] Configure init parameters")
    init_params = sl.InitParameters()
    init_params.set_from_serial_number(serial)
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
    init_params.coordinate_units = sl.UNIT.METER
    # init_params.depth_minimum_distance = 0  # Units equals coordinate_units
    init_params.depth_maximum_distance = 5  # Units equals coordinate_units
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    # init_params.sensing_mode = sl.SENSING_MODE.FILL
    init_params.camera_fps = 30
    init_params.camera_image_flip = sl.FLIP_MODE.OFF

    print(f"[{name}] Open the camera")
    zed = sl.Camera()
    zed_status = zed.open(init_params)
    while zed_status != sl.ERROR_CODE.SUCCESS:
        print(f"[{name}] {repr(zed_status)}")
        zed_status = zed.open(init_params)

    print(f"[{name}] Configure runtime parameters")
    runtime_params = sl.RuntimeParameters()
    # runtime_params.sensing_mode = sl.SENSING_MODE.FILL

    print(f"[{name}] Init sensors data")
    sensors_data = sl.SensorsData()

    resolution = (1280, 720)  # TODO: уменьшить под VGA
    image = sl.Mat(*resolution, sl.MAT_TYPE.U8_C1)
    depth_map = sl.Mat(*resolution, sl.MAT_TYPE.U8_C1)

    save_path = (
        SAVE_PATH + "/" + name + "/" + datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    )
    if not os.path.exists(save_path):
        Path(save_path).mkdir(parents=True, exist_ok=True)

    ts_handler = TimestampHandler()
    photo_counter = 0

    while net.receive():
        if net.id == "PhotoOn":
            if net.msg is None:
                continue

            if net.msg.camera == name:
                is_img_capture = True
                save_path = (
                    SAVE_PATH
                    + "/"
                    + name
                    + "/"
                    + datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
                )
                if not os.path.exists(save_path):
                    Path(save_path).mkdir(parents=True, exist_ok=True)

        if net.id == "PhotoOff":
            if net.msg is None:
                continue

            if net.msg.camera == name:
                is_img_capture = False

        if net.id == "Timer":
            zed_status = zed.grab(runtime_params)
            if zed_status != sl.ERROR_CODE.SUCCESS:
                print(f"[{name}] {repr(zed_status)}")
                continue

            if photo_timer.is_unlock and is_img_capture:
                start = time.time()
                if name == "Front":
                    zed.retrieve_image(image, sl.VIEW.LEFT)
                elif name == "Bottom":
                    zed.retrieve_image(image, sl.VIEW.RIGHT)

                zed.retrieve_image(depth_map, sl.VIEW.DEPTH)

                photo_counter += 1

                file = f"{photo_counter:05d}.png"
                path = f"{save_path}/{file}"

                b, g, r, _ = Image.fromarray(depth_map.get_data()).split()
                png = Image.merge("RGB", (r, g, b))

                if name == "Bottom":
                    png = png.rotate(-90)

                png.save(
                    fp=path, compress_level=3
                )  # quality = 0-100; compress_level= 0-9
                net.send(
                    ImageLink(obj=name, path=path, file=file, counter=photo_counter)
                )

                print(time.time() - start)

            if pose_tracking:
                zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)

                eul = np.zeros((5, 3))  # deg
                vel = np.zeros((5, 3))  # deg/sec

                count = 0
                zed_imu = sensors_data.get_imu_data()

                while count < 5:
                    if not ts_handler.is_new(sensors_data.get_imu_data()):
                        zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)
                        continue
                    zed_imu = sensors_data.get_imu_data()

                    eul[count] = quat2eul(*zed_imu.get_pose().get_orientation().get())
                    eul[count, 1] = min(max(-eul[count, 1] - 90, -90), 90)
                    vel[count] = zed_imu.get_angular_velocity()

                    count += 1

                x, y, z = np.mean(eul, axis=0).tolist()
                vx, vy, vz = np.mean(vel, axis=0).tolist()

                net.send(
                    Sensor(
                        pos_pitch=z,
                        pos_roll=y - ROLL_OFFSET,
                        vel_pitch=vz,
                        vel_roll=-vx,
                    )
                )

                net.send(
                    SensorZ(
                        pos_yaw=-x,
                        vel_yaw=vy,
                    )
                )

    print(f"[{name}] Close the camera")
    zed.close()


if __name__ == "__main__":
    name = sys.argv[1]
    serial = int(sys.argv[2])
    pose_tracking = sys.argv[3] == "True"
    is_stream = len(sys.argv) == 5 and sys.argv[4] == "True"

    main(name=name, serial=serial, is_stream=is_stream, pose_tracking=pose_tracking)
