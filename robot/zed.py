import os
import sys
import threading
import time
from datetime import datetime
from enum import IntFlag
from pathlib import Path
from typing import Callable

import numpy as np
import pyzed.sl as sl
import setproctitle

sys.path.append("./")

import argparse
import logging
from typing import Tuple, Union, List

from base.message import ImageLinkCameraStereo, Sensor, SensorZ
from base.network import Net
from PIL import Image

## CONSTANTS
ROLL_OFFSET = 3.3


class SaveMode(IntFlag):
    Left = 1
    Right = 2
    Depth = 4

    @classmethod
    def get_str(cls) -> str:
        return " ".join([f"'{i._name_}'" for i in cls])


class Action(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[str, List[str]],
        option_string: Union[str, None] = None,
    ) -> None:
        flag_val = SaveMode(0)
        name2val = {i._name_.lower(): i for i in SaveMode}
        vals = [v for val in values for v in val.lower().split("|")]

        for v in vals:
            if v not in name2val.keys():
                raise argparse.ArgumentError(
                    self, f"invalid choice: '{v}' (choose from {SaveMode.get_str()})"
                )
            flag_val |= name2val[v]

        setattr(namespace, self.dest, SaveMode(flag_val))


## END CONSTANTS

## PARSER
parser = argparse.ArgumentParser(
    # prog="Zed camera",
    description="Provide the camera photo and position",
)

parser.add_argument("--serial", type=int, default=0, help="The camera serial number")
parser.add_argument(
    "--camera-orientation",
    required=True,
    choices=["Front", "Bottom"],
    help="The camera orientation",
)
parser.add_argument("--img-capture", action="store_true", help="Enable image capture")
parser.add_argument(
    "--disable-orientation", action="store_true", help="Disable orientation publishing"
)
parser.add_argument(
    "--sensor-buffer", type=int, default=5, help="The amount of data to be approximated"
)
parser.add_argument(
    "--sensor-frequency",
    type=int,
    default=20,
    help="The frequency of receiving data from the sensor in Hz",
)
parser.add_argument(
    "--photo-frequency",
    type=int,
    default=5,
    help="The frequency of image acquisition in Hz",
)
parser.add_argument(
    "--save-mode",
    type=str,
    nargs="+",
    action=Action,
    default=SaveMode.Left,
    help=f"Images saving mode ({SaveMode.get_str()})",
)
parser.add_argument(
    "--save-path", type=str, default="/media/ssd/photo", help="Image save base path"
)
parser.add_argument(
    "--log-level",
    type=str.upper,
    choices=list(logging._levelToName.values()),
    default=logging._levelToName[logging.WARNING],
    help="Logging level",
)

args = parser.parse_args()
## END PARSER


## LOGGER
logging.basicConfig(
    level=logging._nameToLevel[args.log_level],
    format=f"[%(asctime)s] %(levelname)s(%(filename)s | {args.camera_orientation}): %(message)s",
)
## END LOGGER


setproctitle.setproctitle(f"{args.camera_orientation}_{parser.prog}")


def lin_approx(data: np.ndarray, times: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    s_x = np.sum(times)
    s_x2 = np.sum(np.power(times, 2))

    s_y = np.sum(data, axis=0)
    s_xy = np.sum(data * times[..., None], axis=0)
    n = data.shape[0]

    a = (n * s_xy - s_x * s_y) / (n * s_x2 - s_x**2)
    b = (s_y - a * s_x) / n
    return a, b


class TimestampHandler:
    def __init__(self) -> None:
        self.ts = sl.Timestamp()

    def is_new(self, sensor) -> bool:
        is_new = sensor.timestamp.get_microseconds() > self.ts.get_microseconds()
        if is_new:
            self.ts = sensor.timestamp

        return is_new


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


def get_saver(rotate: bool, compress_level: int) -> Callable[[sl.Mat, str], None]:
    def saver(img: sl.Mat, path: str) -> None:
        b, g, r, _ = Image.fromarray(img.get_data()).split()
        png = Image.merge("RGB", (r, g, b))
        if rotate:
            png.rotate(-90)
        png.save(fp=path, compress_level=compress_level)

    return saver


def img_cap(
    *,
    zed,
    camera_orientation: str,
    runtime_params,
    frequency: float = 1 / 5,
    is_img_capture: bool = False,
    save_mode: SaveMode = SaveMode.Left,
    compress_level: int = 3,
) -> None:
    net = Net(frequency)

    save_path = (
        args.save_path
        + "/"
        + camera_orientation
        + "/"
        + datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    )
    if is_img_capture and not os.path.exists(save_path):
        Path(save_path).mkdir(parents=True, exist_ok=True)
    saver = get_saver(camera_orientation == "Bottom", compress_level)

    img = sl.Mat()
    photo_counter = 0

    while net.receive():
        if net.id == "PhotoOn":
            if net.msg is None or net.msg.camera != camera_orientation:
                continue

            logging.info("Image capture enable")

            is_img_capture = True
            save_path = (
                args.save_path
                + "/"
                + camera_orientation
                + "/"
                + datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
            )
            if not os.path.exists(save_path):
                Path(save_path).mkdir(parents=True, exist_ok=True)

        if net.id == "PhotoOff":
            if net.msg is None or net.msg.camera != camera_orientation:
                continue

            logging.info("Image capture disable")
            is_img_capture = False

        if net.id == "Timer" and is_img_capture:
            zed_status = zed.grab(runtime_params)
            if zed_status != sl.ERROR_CODE.SUCCESS:
                logging.warning(f"IMG - {repr(zed_status)}")
                continue

            photo_counter += 1
            file = f"{photo_counter:05d}.png"
            photos = {"left": "", "right": "", "depth": ""}

            if save_mode & SaveMode.Left:
                zed.retrieve_image(img, sl.VIEW.LEFT)
                path = f"{save_path}/left_{file}"
                saver(img, path)

                photos["left"] = path

            if save_mode & SaveMode.Right:
                zed.retrieve_image(img, sl.VIEW.RIGHT)
                path = f"{save_path}/right_{file}"
                saver(img, path)

                photos["right"] = path

            if save_mode & SaveMode.Depth:
                zed.retrieve_image(img, sl.VIEW.DEPTH)
                path = f"{save_path}/depth_{file}"
                saver(img, path)

                photos["depth"] = path

            net.send(
                ImageLinkCameraStereo(
                    obj=camera_orientation,
                    path_left=photos["left"],
                    path_right=photos["right"],
                    path_depth=photos["depth"],
                    counter=photo_counter,
                )
            )


def sensor_cap(
    *, zed, runtime_params, buffer: int = 5, frequency: float = 1 / 20
) -> None:
    net = Net()

    ts_handler = TimestampHandler()
    sensors_data = sl.SensorsData()

    eul = np.zeros((buffer, 3))  # deg
    vel = np.zeros((buffer, 3))  # deg/sec
    times = np.zeros(buffer)

    while True:
        zed_status = zed.grab(runtime_params)
        if zed_status != sl.ERROR_CODE.SUCCESS:
            logging.warning(f"SENSOR - {repr(zed_status)}")
            continue

        count = 0
        while count < 5:
            time.sleep(1 / 400)
            zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)
            zed_imu = sensors_data.get_imu_data()

            if not ts_handler.is_new(zed_imu):
                continue

            eul[count] = quat2eul(*zed_imu.get_pose().get_orientation().get())
            eul[count, 1] = min(max(-eul[count, 1] - 90, -90), 90)
            vel[count] = zed_imu.get_angular_velocity()
            times[count] = ts_handler.ts.get_nanoseconds() - times[(count - 1) % buffer]

            count += 1

        delay = times[-1] - times[-2]

        a, b = lin_approx(eul, times)
        x, y, z = (a * delay + b).tolist()
        a, b = lin_approx(vel, times)
        vx, vy, vz = (a * delay + b).tolist()

        # logging.debug(
        #     f"X: {x:5f}, Y: {y:5f}, Z: {z:5f}, VX: {vx:5f}, VY: {vy:5f}, VZ: {vz:5f}"
        # )

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

        time.sleep(frequency)


def main(
    *,
    name: str,
    serial: int,
    disable_orientation: bool = False,
    is_img_capture: bool = False,
    sensor_buffer: int = 5,
    sensor_frequency: float = 1 / 20,
    photo_frequency: float = 1 / 5,
    save_mode: SaveMode = SaveMode.Left,
) -> None:
    logging.info("Configure init parameters")
    init_params = sl.InitParameters()
    if serial:
        init_params.set_from_serial_number(serial)
    init_params.camera_resolution = sl.RESOLUTION.VGA
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
    init_params.coordinate_units = sl.UNIT.METER
    # init_params.depth_minimum_distance = 0  # Units equals coordinate_units
    init_params.depth_maximum_distance = 5  # Units equals coordinate_units
    init_params.depth_mode = (
        sl.DEPTH_MODE.ULTRA if save_mode & SaveMode.Depth else sl.DEPTH_MODE.NONE
    )
    init_params.camera_fps = int(1 / photo_frequency)
    init_params.camera_image_flip = sl.FLIP_MODE.OFF

    logging.info("Open the camera")
    zed = sl.Camera()
    zed_status = zed.open(init_params)
    while zed_status != sl.ERROR_CODE.SUCCESS:
        logging.warning(f"MAIN - {repr(zed_status)}")
        zed_status = zed.open(init_params)

    logging.info(f"Opened camera: {zed.get_camera_information().serial_number}")

    logging.info("Configure runtime parameters")
    runtime_params = sl.RuntimeParameters()
    # runtime_params.sensing_mode = sl.SENSING_MODE.FILL

    threads = []

    # image
    logging.info("Init image capture thread")
    threads.append(
        threading.Thread(
            target=img_cap,
            kwargs=dict(
                zed=zed,
                runtime_params=runtime_params,
                is_img_capture=is_img_capture,
                frequency=photo_frequency,
                save_mode=save_mode,
                camera_orientation=name,
            ),
        )
    )

    # sensors
    if not disable_orientation:
        logging.info("Init orientation capture thread")
        threads.append(
            threading.Thread(
                target=sensor_cap,
                kwargs=dict(
                    zed=zed,
                    runtime_params=runtime_params,
                    frequency=sensor_frequency,
                    buffer=sensor_buffer,
                ),
            )
        )

    [t.start() for t in threads]

    for t in threads:
        t.join()

    logging.info("Close the camera")
    zed.close()


if __name__ == "__main__":
    logging.info(f"Camera orientation: {args.camera_orientation}")
    logging.info(f"Camera serial number: {args.serial}")
    logging.info(f"Orientation capture: {not args.disable_orientation}")
    logging.info(f"Image capture: {args.img_capture}")
    logging.info(f"Sensor data buffer: {args.sensor_buffer}")
    logging.info(f"Sensor sending frequency: {args.sensor_frequency} Hz")
    logging.info(f"Photo capture frequency: {args.photo_frequency} Hz")
    logging.info(f"Image capture mode: {args.save_mode}")

    main(
        name=args.camera_orientation,
        serial=args.serial,
        disable_orientation=args.disable_orientation,
        is_img_capture=args.img_capture,
        sensor_buffer=args.sensor_buffer,
        sensor_frequency=1 / args.sensor_frequency,
        photo_frequency=1 / args.photo_frequency,
        save_mode=args.save_mode,
    )
