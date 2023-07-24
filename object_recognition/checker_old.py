import datetime
import os

import numpy as np

from image_utils import load_image_rgba, save_image_rgba

#####################
# CONFIG PARAMETERS #
THRESHOLD_COLOR = 75 ** 2
TARGET_COLOR = np.array([129, 179, 41, 255])

THRESHOLD_IMAGE_PART = 0.1

CAMERA_FOV = 70

LOAD_PREFIX_TRUE = 'images/selection/true/'
LOAD_PREFIX_FALSE = 'images/selection/false/'

SAVE_PREFIX = 'images/recognized/'
SAVE_PREFIX_TRUE_POSITIVE = SAVE_PREFIX + 'true_positive'
SAVE_PREFIX_FALSE_POSITIVE = SAVE_PREFIX + 'false_positive'
SAVE_PREFIX_TRUE_NEGATIVE = SAVE_PREFIX + 'true_negative'
SAVE_PREFIX_FALSE_NEGATIVE = SAVE_PREFIX + 'false_negative'


####################


# Function creating a bit mask of the image
def get_mask(pixel):
    error = np.sum(np.square(pixel - TARGET_COLOR))

    return True if error < THRESHOLD_COLOR else False


vec_get_mask = np.vectorize(get_mask, signature='(n)->()')


# Function creating a black and white array image of object
def get_bw(pixel):
    error = np.sum(np.square(pixel - TARGET_COLOR))

    return np.full_like(pixel, 255) if error < THRESHOLD_COLOR else np.full_like(pixel, 0)


vec_get_bw = np.vectorize(get_bw, signature='(n)->(n)')


# Function saving black and white image with detected object for debugging
def save_bw_image(save_path, image, point_coords):
    image_bw_array = vec_get_bw(image)

    image_bw_array[point_coords[0]][point_coords[1]] = np.asarray(np.asarray([255, 0, 0, 255]), dtype='uint8')

    save_image_rgba(save_path, image_bw_array)


def find_obj_image(image_path, is_obj):
    image_array = load_image_rgba(image_path)

    mask = vec_get_mask(image_array)

    y_coords, x_coords = mask.nonzero()

    if len(y_coords) >= THRESHOLD_IMAGE_PART * len(image_array) and is_obj:
        print('found true positive')
        save_prefix = SAVE_PREFIX_TRUE_POSITIVE
    elif len(y_coords) >= THRESHOLD_IMAGE_PART * len(image_array) and not is_obj:
        print('found false positive')
        save_prefix = SAVE_PREFIX_FALSE_POSITIVE
    elif len(y_coords) < THRESHOLD_IMAGE_PART * len(image_array) and is_obj:
        print('found false negative')
        save_prefix = SAVE_PREFIX_TRUE_NEGATIVE
    else:
        print('found true negative')
        save_prefix = SAVE_PREFIX_FALSE_NEGATIVE

    original_path = f"{save_prefix}/{image_file}"
    save_image_rgba(original_path, image_array)

    # Saving black and white image with detected object for debugging
    if len(x_coords) and len(y_coords):
        obj_x, obj_y = round(np.average(x_coords)), round(np.average(y_coords))
    else:
        obj_x, obj_y = 0, 0

    bw_file = image_file.replace('.jpg', '_bw.jpg')
    bw_path = f"{save_prefix}/{bw_file}"

    save_bw_image(bw_path, image_array, (obj_x, obj_y))


for image_file in sorted(os.listdir(LOAD_PREFIX_TRUE)):
    find_obj_image(LOAD_PREFIX_TRUE + image_file, True)

for image_file in sorted(os.listdir(LOAD_PREFIX_FALSE)):
    find_obj_image(LOAD_PREFIX_FALSE + image_file, False)
