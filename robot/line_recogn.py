import math
import sys
import time
import setproctitle

from base import network, message
from base.mat import calc_lin_approx, line_closest_point

from object_recognition.model_class import RGBModel, HSVModel, get_model_path
from object_recognition.image_utils import load_image_rgb, save_image_rgb, crop
from object_recognition.config import *

import numpy as np

#####################
# CONFIG PARAMETERS #
MODEL_PATH_PREFIX = '../object_recognition/'

# Value which would be used in received path dictionary
CAMERA_FOV = 51

DEBUG = True


####################


# Calculate how big should be image to contain given space in real world
def meters_to_pixels(meters, distance, fov, image_side):
    return image_side * meters / distance / (2 * math.tan(fov / 2))


def main(camera_name, model_name, camera_eye, line_depth, visible_range):
    """
    :param camera_name:
    :param model_name:
    :param camera_eye: left, right or depth
    :param line_depth:
    :param visible_range: side of visible area of the floor
    :return:
    """
    if COLOR_SCHEME == 'HSV':
        model = HSVModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    elif COLOR_SCHEME == "RGB":
        model = RGBModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    else:
        raise Exception

    if camera_name != 'Bottom':
        raise "Wrong camera name"

    current_depth = 0

    net = network.Net()
    while net.receive():
        if net.id == "ImageLinkCameraStereo":
            if net.msg.obj == camera_name:
                time1 = time.time()

                image = load_image_rgb(net.msg.path[camera_eye])

                smaller_side = min(image.shape[:2])
                image = crop(image, (smaller_side, smaller_side))

                new_size = int(meters_to_pixels(
                    visible_range,
                    line_depth - current_depth,
                    CAMERA_FOV,
                    image.shape[0]
                ))
                image = crop(image, (new_size, new_size))

                try:
                    is_obj_found = model.check_object(image)
                except Exception as e:
                    print(image)
                    print(f'Распознавалка упала с ошибкой {e}')
                    continue

                shape = image.shape
                image_mask = model.image_weight

                # Creating auxiliary array to filter zero sums
                auxiliary_sum = np.stack((
                    np.arange(shape[0]),
                    image_mask @ np.arange(shape[1]),
                    np.sum(image_mask, axis=1)
                ))
                filtered_sum = auxiliary_sum[:, auxiliary_sum[2] != 0]

                filtered_indexes = filtered_sum[0].astype('uint64')

                mean_x_vector = (filtered_sum[1] // filtered_sum[2]).astype('uint64')

                if mean_x_vector.size > 1:
                    a, b = calc_lin_approx((filtered_indexes, mean_x_vector))
                else:
                    a, b = 0, shape[1] / 2

                if DEBUG:
                    save_path = net.msg.path[camera_eye].replace('.png', '_line.png')

                    image_debug = model.get_debug()

                    image_debug[filtered_indexes, mean_x_vector] = 255, 255, 0

                    line_ys = np.arange(shape[0])
                    line_xs = (a * np.arange(shape[0]) + b).astype('int64')

                    line_indexes = np.stack((line_ys, line_xs))
                    line_indexes = line_indexes[
                                   :,
                                   (line_indexes[1, :] >= 0) & (line_indexes[1, :] < image_debug.shape[1])
                                   ]

                    image_debug[line_indexes[0], line_indexes[1]] = 255, 0, 0

                    save_image_rgb(save_path, image_debug)

                    net.send(message.ImageLinkRecognition(
                        obj=camera_name + 'Line',
                        path=save_path,
                        counter=None
                    ))

                if is_obj_found:
                    # x, y in line coordinate system
                    x, y = line_closest_point(
                        (a, b),
                        (shape[0] / 2, shape[1] / 2)
                    )

                    lag_error = (y / shape[1] - 0.5) * visible_range

                    yaw_error = math.degrees(math.atan(a))

                    net.send(message.Line(
                        is_detected=True,
                        image_shape=image.shape,
                        lag_error=lag_error,
                        yaw_error=yaw_error,
                        counter=0
                    ))

                else:
                    net.send(message.Line(is_detected=False, image_shape=image.shape))

                time2 = time.time()
                if time2 - time1 > 0.25:
                    print(f"Image recognition slower than 0.25s: {time2 - time1}")

        elif net.id == 'Coord':
            current_depth = net.msg.pos[2]


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(
        camera_name=sys.argv[1],
        model_name=sys.argv[2],
        camera_eye=sys.argv[3],
        line_depth=float(sys.argv[4]),
        visible_range=float(sys.argv[5])
    )
