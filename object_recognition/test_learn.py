import os
import time

import numpy as np

from image_utils import load_image_rgba, save_image_rgba, save_image_rgb
from model_class import COLOR_AMOUNT, COLOR_COMPRESSION, OBJ

#####################
# CONFIG PARAMETERS #
PIXEL_AREA = 0

LOAD_PREFIX = 'images/selection_learn/'
LOAD_PREFIX_OBJ = LOAD_PREFIX + OBJ + '/'

SAVE_PREFIX = 'images/selection_learn/'


#####################


def inc_pixel_data(model, index):
    model[index] += 1


data_all = np.zeros((COLOR_AMOUNT ** 3))
data_found = np.zeros((COLOR_AMOUNT ** 3))
data_not_found = np.zeros((COLOR_AMOUNT ** 3))

for image_name in os.listdir(LOAD_PREFIX_OBJ):
    if not image_name.startswith('learning') or 'out' in image_name:
        continue

    time1 = time.time()
    image = load_image_rgba(LOAD_PREFIX_OBJ + image_name)
    print(f"Image loaded: {time.time() - time1}")

    time2 = time.time()
    r_layer, g_layer, b_layer, a_layer = [
        np.asarray(image[:, :, i] // COLOR_COMPRESSION, dtype='uint8') for i in range(4)
    ]

    index_matrix = r_layer * COLOR_AMOUNT ** 2 + g_layer * COLOR_AMOUNT + b_layer

    inc_pixel_data(data_all, index_matrix)
    inc_pixel_data(data_found, index_matrix[(a_layer < 128).nonzero()])
    inc_pixel_data(data_found, index_matrix[(a_layer >= 128).nonzero()])

    print(f"Image processed: {time.time() - time2}")

    time3 = time.time()
    r_layer_bw = np.where(image[:, :, 3] < 128, r_layer, 255)
    g_layer_bw = np.where(image[:, :, 3] < 128, r_layer, 255)
    b_layer_bw = np.where(image[:, :, 3] < 128, r_layer, 255)
    image_obj = np.dstack((r_layer_bw, g_layer_bw, b_layer_bw))

    print(f'Image bw generated: {time.time() - time3}')

    time4 = time.time()
    save_image_rgb(LOAD_PREFIX_OBJ + image_name.replace('.png', '_out.png'), image_obj)
    print(f"Image saved: {time.time() - time4}")

    print(f"Total: {time.time() - time1}")

print(data_not_found.dtype, data_found.dtype, data_all.dtype)
np.save('model_found.npy', data_found)
np.save('model_not_found.npy', data_not_found)
np.save('model_all.npy', data_all)

np.save('model_divided.npy', (data_found / np.where(data_all > 0, data_all, 1)))
