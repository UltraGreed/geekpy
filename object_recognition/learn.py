import os
import time

import numpy as np

from image_utils import load_image_rgba, save_image_rgba, save_image_rgb
from model_class import COLOR_AMOUNT, COLOR_COMPRESSION, OBJ, PIXEL_AREA
from model_class import get_model_path

#####################
# CONFIG PARAMETERS #
LOAD_PREFIX = 'images/selection_learn/'
LOAD_PREFIX_OBJ = LOAD_PREFIX + OBJ + '/'

SAVE_PREFIX = 'images/selection_learn/'
#####################


def inc_pixel_data(model, index):
    for dx in range(-PIXEL_AREA, PIXEL_AREA + 1):
        for dy in range(-PIXEL_AREA, PIXEL_AREA + 1):
            for dz in range(-PIXEL_AREA, PIXEL_AREA + 1):
                index_delta = index + dx * COLOR_AMOUNT ** 2 + dy * COLOR_AMOUNT + dz
                np.add.at(model, index_delta[np.logical_and(index_delta >= 0, index_delta < data_all.shape[0])], 1)


data_all = np.zeros((COLOR_AMOUNT ** 3))
data_object = np.zeros((COLOR_AMOUNT ** 3))
data_non_object = np.zeros((COLOR_AMOUNT ** 3))

for image_name in os.listdir(LOAD_PREFIX_OBJ):
    if not image_name.startswith('learning') or 'out' in image_name:
        continue

    time1 = time.time()
    image = load_image_rgba(LOAD_PREFIX_OBJ + image_name)
    print(f"Image loaded: {time.time() - time1}")

    time2 = time.time()
    r_layer, g_layer, b_layer = [
        np.asarray(image[:, :, i] // COLOR_COMPRESSION, dtype='uint32') for i in range(3)
    ]
    a_layer = image[:, :, 3]

    index_matrix = r_layer * COLOR_AMOUNT ** 2 + g_layer * COLOR_AMOUNT + b_layer

    inc_pixel_data(data_all, index_matrix)
    inc_pixel_data(data_object, index_matrix[a_layer < 128])
    inc_pixel_data(data_non_object, index_matrix[a_layer >= 128])

    print(f"Image processed: {time.time() - time2}")

    time3 = time.time()
    r_layer_bw = np.where(image[:, :, 3] < 128, a_layer, 255)
    g_layer_bw = np.where(image[:, :, 3] < 128, g_layer, 255)
    b_layer_bw = np.where(image[:, :, 3] < 128, b_layer, 255)
    image_obj = np.dstack((r_layer_bw, g_layer_bw, b_layer_bw))

    print(f'Image bw generated: {time.time() - time3}')

    time4 = time.time()
    save_image_rgb(LOAD_PREFIX_OBJ + image_name.replace('.png', '_out.png'), np.asarray(image_obj, dtype='uint8'))
    print(f"Image saved: {time.time() - time4}")

    print(f"Total: {time.time() - time1}")

print(data_non_object.dtype, data_object.dtype, data_all.dtype)
np.save(get_model_path('obj'), data_object)
np.save(get_model_path('noobj'), data_non_object)
np.save(get_model_path('all'), data_all)