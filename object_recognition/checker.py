import os
import glob

import numpy as np

from image_utils import load_image_rgba, save_image_rgba

from model_class import Model

#####################
# CONFIG PARAMETERS #
LOAD_PREFIX = 'images/selection_test/CellB/'
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
    image = load_image_rgba(image_path)

    is_obj_found = model.check_object(image)

    if is_obj_found and is_obj:
        print('found true positive', end=' ')
        save_prefix = SAVE_PREFIX_TRUE_POSITIVE
    elif is_obj_found and not is_obj:
        print('found false positive', end=' ')
        save_prefix = SAVE_PREFIX_FALSE_POSITIVE
    elif not is_obj_found and is_obj:
        print('found false negative', end=' ')
        save_prefix = SAVE_PREFIX_FALSE_NEGATIVE
    else:
        print('found true negative', end=' ')
        save_prefix = SAVE_PREFIX_TRUE_NEGATIVE

    print(image_file)

    # Copying original image according to our model
    original_path = save_prefix + image_file
    save_image_rgba(original_path, image)

    # Saving black and white image with detected object for debugging

    obj_x, obj_y = model.object_center if model.check_object() else (0, 0)

    bw_file = image_file.replace('.jpg', '_grayscale.png')
    bw_path = save_prefix + bw_file

    image_bw_array = model.get_grayscale(image)

    image_bw_array[int(obj_x + 0.5)][int(obj_y + 0.5)] = np.asarray([255, 0, 0, 255], dtype='uint8')

    save_image_rgba(bw_path, image_bw_array)


for directory in (
        SAVE_PREFIX_TRUE_NEGATIVE,
        SAVE_PREFIX_FALSE_NEGATIVE,
        SAVE_PREFIX_TRUE_POSITIVE,
        SAVE_PREFIX_FALSE_POSITIVE
):
    clear_dir(directory)

model = Model('model_divided.npy')

for image_file in sorted(os.listdir(LOAD_PREFIX_TRUE)):
    find_obj_image(LOAD_PREFIX_TRUE + image_file, True)

for image_file in sorted(os.listdir(LOAD_PREFIX_FALSE)):
    find_obj_image(LOAD_PREFIX_FALSE + image_file, False)
