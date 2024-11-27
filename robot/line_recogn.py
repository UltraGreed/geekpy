import math
import sys
import time
from pathlib import Path

import setproctitle

from base import network, message
from base.mat import line_closest_point

from object_recognition.model_class import RGBModel, HSVModel, get_model_path
from object_recognition.image_utils import load_image_rgb, save_image_rgb, crop, meters_to_pixels
from object_recognition.config import *

import numpy as np

#####################
# CONFIG PARAMETERS #
MODEL_PATH_PREFIX = '../object_recognition/'

# Value which would be used in received path dictionary
CAMERA_FOV = 51

DEBUG = True
####################


def main(camera_path: str, model_name: str, visible_range: float):
    """
    Receive images from camera, inference line and send yaw and lag offsets.

    :param camera_path: camera.eye to listen to
    :param model_name: np model to use in inference
    :param visible_range: side of visible area of the floor
    :return:
    """
    camera_name, camera_eye = camera_path.split('.')
    if COLOR_SCHEME == 'HSV':
        model = HSVModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    elif COLOR_SCHEME == 'RGB':
        model = RGBModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    else:
        raise Exception

    if camera_name != 'Bottom':
        raise Exception('Wrong camera name')

    current_depth = 0
    line_depth = network.wait_message(message.FilteredObjects.id).objs['Line'][2]

    net = network.Net()
    while net.receive():
        if net.id == 'ImageLinkCameraStereo' and net.msg.obj == camera_name:
            time1 = time.time()

            image = load_image_rgb(net.msg.path[camera_eye])

            smaller_side = min(image.shape[:2])
            image = crop(image, (smaller_side, smaller_side))

            new_size = int(
                meters_to_pixels(
                    visible_range, line_depth - current_depth, CAMERA_FOV, image.shape[1]
                )
            )
            shape_ratio = image.shape[0] / image.shape[1]
            image = crop(image, (int(new_size * shape_ratio), new_size))

            if image.size == 0:
                print('Пустой image в line_recogn.py')
                continue

            is_obj_found = model.check_object(image)

            shape = image.shape
            image_mask = model.image_weight

            # Filtering rows with zero sum
            row_sums = np.sum(image_mask, axis=1, dtype=MODEL_NEXT_DTYPE)
            nonzero_mask = row_sums != 0

            rows = np.arange(shape[0], dtype=np.uint16)[nonzero_mask]
            row_weighted_sums = np.matmul(
                image_mask,
                np.arange(shape[1], dtype=np.uint16),
                dtype=MODEL_NEXT_DTYPE
            )[nonzero_mask]
            row_means = row_weighted_sums / row_sums[nonzero_mask]

            if row_means.size > 1:
                a, b = np.linalg.lstsq(
                    np.vstack((rows, np.ones_like(rows))).T,
                    row_means
                )[0]
            else:
                a, b = 0, shape[1] / 2

            if DEBUG:
                original_filename = Path(net.msg.path[camera_eye]).with_suffix('')
                original_ext = Path(net.msg.path[camera_eye]).suffix

                save_path = f'{original_filename}_Line_debug{original_ext}'

                image_debug = model.get_debug()

                image_debug[rows, row_means.astype(np.uint64)] = 255, 255, 0

                line_ys = np.arange(shape[0])
                line_xs = (a * np.arange(shape[0]) + b).astype(np.int64)

                line_indexes = np.stack((line_ys, line_xs))
                line_indexes = line_indexes[
                    :, (line_indexes[1, :] >= 0) & (line_indexes[1, :] < image_debug.shape[1])
                ]

                image_debug[line_indexes[0], line_indexes[1]] = 255, 0, 0

                save_image_rgb(save_path, image_debug)

                net.send(
                    message.ImageLinkRecognition(
                        obj=camera_name + 'Line', path=save_path, counter=None
                    )
                )

            if is_obj_found:
                # x, y in line coordinate system
                x, y = line_closest_point((a, b), (shape[0] / 2, shape[1] / 2))

                lag_error = (y / shape[1] - 0.5) * visible_range

                yaw_error = math.degrees(math.atan(a))

                net.send(
                    message.Line(
                        is_detected=True,
                        image_shape=image.shape,
                        lag_error=lag_error,
                        yaw_error=yaw_error,
                        counter=0,
                    )
                )

            else:
                net.send(message.Line(is_detected=False, image_shape=image.shape))

            time2 = time.time()
            if time2 - time1 > 0.25:
                print(f'Image recognition slower than 0.25s: {time2 - time1}')

        elif net.id == 'Coord':
            current_depth = net.msg.pos[2]


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(camera_path=sys.argv[1], model_name=sys.argv[2], visible_range=float(sys.argv[3]))
