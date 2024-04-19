import os
import sys
# from typing import Literal

import cv2
import cv2.aruco as aruco
import numpy as np
import setproctitle

sys.path.append("./")

from base import network
from base.message import (
    YAW,
    Coord,
    DetectedObject,
    ImageLinkCameraStereo,
    ImageLinkRecognition,
)

setproctitle.setproctitle(sys.argv[0])


def aruco_bboxes(
    img: np.ndarray,
    markerSize = 4,
    totalMarkers = 50,
    to_gray: bool = True,
) -> np.ndarray:
    if to_gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(
        aruco,
        f"DICT_{markerSize}X{markerSize}_{totalMarkers}",
        aruco.DICT_ARUCO_ORIGINAL,
    )

    arucoDict = aruco.getPredefinedDictionary(key)
    arucoParam = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(arucoDict, arucoParam)

    bboxes, _, _ = detector.detectMarkers(img)

    # Returns xyhw for all detected aruco codes, otherwise an array with shape = (0, )
    return np.array([box[0] for box in bboxes], dtype=int)


def draw_center(img: np.ndarray, bbox: np.ndarray, radius: int = 50) -> np.ndarray:
    center = ((bbox[0] + bbox[-2]) // 2)[None]
    vecs = center - bbox
    vecs = vecs / np.linalg.norm(vecs)

    rect = (center + vecs * radius).astype(int)

    return cv2.fillPoly(
        img,
        pts=rect[None],
        color=(255, 255, 255),
    )


def calc_direction(direction_aruco: np.ndarray) -> float:
    return (180 - np.rad2deg(np.arccos(direction_aruco[1]))) * np.sign(
        direction_aruco[0]
    )


def main():
    net = network.Net(1 / 10)
    counter = 0

    robot: list[float] = network.wait_message(Coord.id).pos

    while net.receive():
        if net.id == ImageLinkCameraStereo.id:
            msg: ImageLinkCameraStereo = net.msg
            for path in msg.path.values():
                img = cv2.imread(path)
                bboxes = aruco_bboxes(img, totalMarkers=250)

                if not len(bboxes):
                    continue

                mask = np.zeros_like(img)
                direction = 0.0
                for bbox in bboxes:
                    mask = draw_center(mask, bbox, radius=50)

                    aruco_direct = bbox[0] - bbox[-1]
                    aruco_direct = aruco_direct / np.linalg.norm(aruco_direct)
                    direction = calc_direction(aruco_direct)

                mask_path = f"{os.path.dirname(path)}/aruco_mask_{counter}.png"
                cv2.imwrite(mask_path, mask)
                net.send(ImageLinkRecognition("Aruco", path=mask_path, counter=counter))
                counter += 1

                net.send(
                    DetectedObject("Aruco", yaw=robot[YAW] + direction, is_seen=True)
                )

        elif net.id == Coord.id:
            robot = net.msg.pos


def real_time():
    cap = cv2.VideoCapture(0)
    while True:
        _, img = cap.read()

        bboxes = aruco_bboxes(img, totalMarkers=250)
        mask = img.copy()

        for bbox in bboxes:
            # Center mask
            mask = draw_center(mask, bbox, radius=50)

            direction_aruco = bbox[0] - bbox[-1]
            direction_aruco = direction_aruco / np.linalg.norm(direction_aruco)

            # Direction
            cv2.line(
                mask,
                bbox[0],
                (bbox[0] + direction_aruco * 20).astype(int),
                color=(0, 0, 255),
                thickness=2,
            )

            # Border
            cv2.polylines(
                mask,
                bbox[None],
                isClosed=True,
                color=(255, 0, 0),
                thickness=2,
            )

        cv2.imshow("img", mask)
        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    # real_time()
