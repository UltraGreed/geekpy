import sys
import time
import setproctitle

from base import network, message
from base.mat import calc_lin_approx

from object_recognition.model_class import RGBModel, HSVModel, get_model_path
from object_recognition.image_utils import load_image_rgb, save_image_rgb
from object_recognition.object_position import get_yaw_from_pixel
from object_recognition.config import *

import numpy as np

#####################
# CONFIG PARAMETERS #
MODEL_PATH_PREFIX = '../object_recognition/'

# Value which would be used in received path dictionary
PATH_PARAMETER = 'right'

DEBUG = True


####################


def main(camera_name, model_type, model_name):
    if COLOR_SCHEME == 'HSV':
        model = HSVModel(MODEL_PATH_PREFIX + get_model_path(model_type, model_name))
    elif COLOR_SCHEME == "RGB":
        model = RGBModel(MODEL_PATH_PREFIX + get_model_path(model_type, model_name))
    else:
        raise Exception

    net = network.Net()
    while net.receive():
        if net.id == "ImageLinkCameraStereo":
            if net.msg.obj == camera_name:
                time1 = time.time()
                image = np.rot90(load_image_rgb(net.msg.path[PATH_PARAMETER]), 3)
                is_obj_found = model.check_object(image)

                image_mask = model.image_weight
                shape = image_mask.shape

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
                    a, b = 1, 0

                if DEBUG:
                    save_path = net.msg.path[PATH_PARAMETER].replace('.png', '_line.png')

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
                    if camera_name != 'Bottom':
                        raise "Wrong camera name"

                    net.send(message.Line(
                        coefs=(float(a), float(b)),
                        image_shape=image.shape,
                        is_detected=True,
                        counter=0
                    ))

                else:
                    net.send(message.Line(is_detected=False, image_shape=image.shape))

                time2 = time.time()
                if time2 - time1 > 0.25:
                    print(f"Image recognition slower than 0.25s: {time2 - time1}")


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(camera_name=sys.argv[1], model_type=sys.argv[2], model_name=sys.argv[3])
