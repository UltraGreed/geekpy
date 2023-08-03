import math
import os
import time

import numpy as np

from image_utils import load_image_rgba, save_image_rgb
from model_class import COLOR_AMOUNT, COLOR_COMPRESSION, OBJ, PIXEL_AREA
from model_class import get_model_learn_path

#####################
# CONFIG PARAMETERS #
LOAD_PREFIX = 'images/selection_learn/'
LOAD_PREFIX_OBJ = LOAD_PREFIX + OBJ + '/'

SAVE_PREFIX = 'images/selection_learn/'


#####################


def inc_pixel_data(model, index):
    dx, dy, dz = [np.arange(-PIXEL_AREA, PIXEL_AREA + 1) for _ in range(3)]

    dx_mesh, dy_mesh, dz_mesh = np.meshgrid(dx, dy, dz)

    dist_matrix = np.square(dx_mesh) + np.square(dy_mesh) + np.square(dz_mesh)

    offset_matrix = dx_mesh * COLOR_AMOUNT ** 2 + dy_mesh * COLOR_AMOUNT + dz_mesh

    result_index = np.sum(np.meshgrid(index, offset_matrix[dist_matrix <= PIXEL_AREA ** 2].flatten()), axis=0)

    np.add.at(
        model,
        result_index[np.logical_and(result_index >= 0, result_index < data_all.shape[0])],
        1
    )


data_all = np.zeros((COLOR_AMOUNT ** 3))
data_object = np.zeros((COLOR_AMOUNT ** 3))
data_non_object = np.zeros((COLOR_AMOUNT ** 3))

for image_name in os.listdir(LOAD_PREFIX_OBJ):
    if 'out' in image_name:
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
np.save(get_model_learn_path('obj'), data_object)
np.save(get_model_learn_path('noobj'), data_non_object)
np.save(get_model_learn_path('all'), data_all)
