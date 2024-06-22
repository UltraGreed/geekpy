import os
import sys

import cv2
import cv2.aruco as aruco
import numpy as np
import setproctitle
from pathlib import Path

from base import network
from base.message import (
    YAW,
    DEPTH,
    Coord,
    DetectedObject,
    FilteredObjects,
    ImageLinkCameraStereo,
    ImageLinkRecognition,
)

from object_recognition.object_position import get_obj_pos_bottom


DEBUG = True


def aruco_bboxes(
    img: np.ndarray,
    markerSize=4,
    totalMarkers=50,
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


def get_center(bbox: np.ndarray) -> np.ndarray:
    return np.flip((bbox[0] + bbox[-2]) // 2)


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
    return (180 - np.rad2deg(np.arccos(direction_aruco[1]))) * np.sign(direction_aruco[0])


def main(camera_path: str, object_name: str):
    camera_name, camera_eye = camera_path.split('.')

    net = network.Net(1 / 10)
    counter = 0

    robot: list[float] = network.wait_message(Coord.id).pos
    depth: float = network.wait_message(FilteredObjects.id).objs[object_name][DEPTH]

    while net.receive():
        if net.id == ImageLinkCameraStereo.id and net.msg.obj == camera_name:
            msg: ImageLinkCameraStereo = net.msg

            path = msg.path[camera_eye]

            img = cv2.imread(path)
            bboxes = aruco_bboxes(img, totalMarkers=250)

            if bboxes.size > 0:
                direction = 0.0

                for bbox in bboxes:
                    aruco_direct = bbox[0] - bbox[-1]
                    aruco_direct = aruco_direct / np.linalg.norm(aruco_direct)
                    direction += calc_direction(aruco_direct)

                center = get_center(bboxes[0])

                x, y, _ = get_obj_pos_bottom(robot, depth, img.shape, center)

                net.send(
                    DetectedObject(object_name, x=float(x), y=float(y), yaw=float(robot[YAW] + direction))
                )

            if DEBUG:
                mask = np.zeros_like(img)
                if bboxes.size > 0:
                    for bbox in bboxes:
                        # Direction
                        cv2.line(
                            mask,
                            np.flip(center),
                            (np.flip(center) + aruco_direct * 30).astype(int),
                            color=(0, 0, 255),
                            thickness=2,
                        )
                        mask = draw_center(mask, bbox, radius=50)
                else:
                    # Draw cross if not recognized
                    cv2.line(
                        mask,
                        (0, 0),
                        (img.shape[1] - 1, img.shape[0] - 1),
                        color=(0, 0, 255),
                        thickness=2,
                    )
                    cv2.line(
                        mask,
                        (0, img.shape[0] - 1),
                        (img.shape[1] - 1, 0),
                        color=(0, 0, 255),
                        thickness=2,
                    )

                mask_path = f"{os.path.dirname(path)}/{Path(path).stem}_mask_aruco.png"
                cv2.imwrite(mask_path, mask)

                net.send(ImageLinkRecognition(object_name, path=mask_path, counter=counter))

                counter += 1

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
    sys.path.append("./")
    setproctitle.setproctitle(sys.argv[0])

    main(
        camera_path=sys.argv[1],
        object_name=sys.argv[2]
    )
