import os
import glob

import numpy as np

from image_utils import load_image_rgba, save_image_rgba

from model_class import Model

#####################
# CONFIG PARAMETERS #
THRESHOLD_IMAGE_PART = 0.1

THRESHOLD_MIN = 0.99
THRESHOLD_MAX = 0.999

COLOR_AMOUNT = 64
COLOR_COMPRESSION = 256 / COLOR_AMOUNT

LOAD_PREFIX = 'images/selection_test/YScotch/'
LOAD_PREFIX_TRUE = LOAD_PREFIX + 'true/'
LOAD_PREFIX_FALSE = LOAD_PREFIX + 'false/'

SAVE_PREFIX = 'images/result_test/'
SAVE_PREFIX_TRUE_POSITIVE = SAVE_PREFIX + 'true_positive/'
SAVE_PREFIX_FALSE_POSITIVE = SAVE_PREFIX + 'false_positive/'
SAVE_PREFIX_TRUE_NEGATIVE = SAVE_PREFIX + 'true_negative/'
SAVE_PREFIX_FALSE_NEGATIVE = SAVE_PREFIX + 'false_negative/'
####################


def clear_dir(path):
    files = glob.glob(f'{path}*')
    for file in files:
        os.remove(file)


def find_obj_image(image_path, is_obj):
    image_array = load_image_rgba(image_path)

    mask = model.get_mask(image_array)

    y_coords, x_coords = mask.nonzero()

    threshold_pixel_amount = THRESHOLD_IMAGE_PART * len(image_array) ** 2

    if len(y_coords) >= threshold_pixel_amount and is_obj:
        print('found true positive', end=' ')
        save_prefix = SAVE_PREFIX_TRUE_POSITIVE
    elif len(y_coords) >= threshold_pixel_amount and not is_obj:
        print('found false positive', end=' ')
        save_prefix = SAVE_PREFIX_FALSE_POSITIVE
    elif len(y_coords) < threshold_pixel_amount and is_obj:
        print('found false negative', end=' ')
        save_prefix = SAVE_PREFIX_FALSE_NEGATIVE
    else:
        print('found true negative', end=' ')
        save_prefix = SAVE_PREFIX_TRUE_NEGATIVE

    print(image_file)

    # Copying original image according to our model
    original_path = save_prefix + image_file
    save_image_rgba(original_path, image_array)

    # Saving black and white image with detected object for debugging
    if len(x_coords) and len(y_coords):
        obj_x, obj_y = round(np.average(x_coords)), round(np.average(y_coords))
    else:
        obj_x, obj_y = 0, 0

    bw_file = image_file.replace('.jpg', '_grayscale.png')
    bw_path = save_prefix + bw_file

    image_bw_array = model.get_grayscale(image_array)

    image_bw_array[obj_x][obj_y] = np.asarray([255, 0, 0, 255], dtype='uint8')

    save_image_rgba(bw_path, image_bw_array)


for directory in (
        SAVE_PREFIX_TRUE_NEGATIVE,
        SAVE_PREFIX_FALSE_NEGATIVE,
        SAVE_PREFIX_TRUE_POSITIVE,
        SAVE_PREFIX_FALSE_POSITIVE
):
    clear_dir(directory)

model = Model()

for image_file in sorted(os.listdir(LOAD_PREFIX_TRUE)):
    find_obj_image(LOAD_PREFIX_TRUE + image_file, True)

for image_file in sorted(os.listdir(LOAD_PREFIX_FALSE)):
    find_obj_image(LOAD_PREFIX_FALSE + image_file, False)
