import os
import glob

import numpy as np

from image_utils import load_image_rgba, save_image_rgba

#####################
# CONFIG PARAMETERS #
THRESHOLD_IMAGE_PART = 0.1

THRESHOLD_MIN = 0.8
THRESHOLD_MAX = 0.95

COLOR_AMOUNT = 64
COLOR_COMPRESSION = 256 / COLOR_AMOUNT

LOAD_PREFIX_TRUE = 'images/selection_test/true/'
LOAD_PREFIX_FALSE = 'images/selection_test/false/'

SAVE_PREFIX = 'images/recognized/'
SAVE_PREFIX_TRUE_POSITIVE = SAVE_PREFIX + 'true_positive/'
SAVE_PREFIX_FALSE_POSITIVE = SAVE_PREFIX + 'false_positive/'
SAVE_PREFIX_TRUE_NEGATIVE = SAVE_PREFIX + 'true_negative/'
SAVE_PREFIX_FALSE_NEGATIVE = SAVE_PREFIX + 'false_negative/'
####################


def get_model_data(pixel):
    x, y, z = [round(i / COLOR_COMPRESSION) for i in [
        pixel[0],
        pixel[1],
        pixel[2]
    ]]
    return model[x][y][z]


# Function creating a bit mask of the image
def get_mask(pixel):
    return get_model_data(pixel) >= model_upper_border


vec_get_mask = np.vectorize(get_mask, signature='(n)->()')


# Function creating a black and white array image of object
def get_grayscale(pixel):
    value = get_model_data(pixel)

    if value <= model_lower_border:
        alpha = 0
    elif value >= model_upper_border:
        alpha = 255
    else:
        alpha = 255 * (value - model_lower_border) / (model_upper_border - model_lower_border)

    gray_pixel = np.asarray([0, 255, 0, alpha], dtype='uint8')

    return gray_pixel


vec_get_grayscale = np.vectorize(get_grayscale, signature='(n)->(n)')


def clear_dir(path):
    files = glob.glob(f'{path}*')
    for file in files:
        os.remove(file)


def find_obj_image(image_path, is_obj):
    image_array = load_image_rgba(image_path)

    mask = vec_get_mask(image_array)

    y_coords, x_coords = mask.nonzero()

    if len(y_coords) >= THRESHOLD_IMAGE_PART * len(image_array) and is_obj:
        print('found true positive', end=' ')
        save_prefix = SAVE_PREFIX_TRUE_POSITIVE
    elif len(y_coords) >= THRESHOLD_IMAGE_PART * len(image_array) and not is_obj:
        print('found false positive', end=' ')
        save_prefix = SAVE_PREFIX_FALSE_POSITIVE
    elif len(y_coords) < THRESHOLD_IMAGE_PART * len(image_array) and is_obj:
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

    image_bw_array = vec_get_grayscale(image_array)

    image_bw_array[obj_x][obj_y] = np.asarray([255, 0, 0, 255], dtype='uint8')

    save_image_rgba(bw_path, image_bw_array)


for directory in (
        SAVE_PREFIX_TRUE_NEGATIVE,
        SAVE_PREFIX_FALSE_NEGATIVE,
        SAVE_PREFIX_TRUE_POSITIVE,
        SAVE_PREFIX_FALSE_POSITIVE
):
    clear_dir(directory)

model = np.load('model.npy')

model_max = np.max(model)
model_min = np.min(model)

model_lower_border = round(model_min + THRESHOLD_MIN * (model_max - model_min))
model_upper_border = round(model_min + THRESHOLD_MAX * (model_max - model_min))

for image_file in sorted(os.listdir(LOAD_PREFIX_TRUE)):
    find_obj_image(LOAD_PREFIX_TRUE + image_file, True)

for image_file in sorted(os.listdir(LOAD_PREFIX_FALSE)):
    find_obj_image(LOAD_PREFIX_FALSE + image_file, False)
