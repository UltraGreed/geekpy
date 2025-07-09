import sys
import time
from pathlib import Path

import numpy as np

from image_utils import load_image_rgba, rgba_to_hsv
from model_class import get_model_path

from config import (
    PIXEL_AREA,
    RGB_AMOUNT,
    RGB_COMPRESSION,
    H_AMOUNT,
    S_AMOUNT,
    V_AMOUNT,
    H_COMPRESSION,
    S_COMPRESSION,
    V_COMPRESSION,
    TRAIN_DTYPE,
    MODEL_SHAPE,
    COLOR_SCHEME,
)


#####################
# CONFIG PARAMETERS #
LOAD_PREFIX = Path('images/selection_train/')
#####################


def inc_data_rgb(model, index, max_len):
    dx, dy, dz = (np.arange(-PIXEL_AREA, PIXEL_AREA + 1) for _ in range(3))

    dx_mesh, dy_mesh, dz_mesh = np.meshgrid(dx, dy, dz)

    dist_matrix = np.square(dx_mesh) + np.square(dy_mesh) + np.square(dz_mesh)

    offset_matrix = dx_mesh * RGB_AMOUNT**2 + dy_mesh * RGB_AMOUNT + dz_mesh

    result_index = np.sum(
        np.meshgrid(index, offset_matrix[dist_matrix <= PIXEL_AREA**2].flatten()), axis=0
    )

    np.add.at(model, result_index[np.logical_and(result_index >= 0, result_index < max_len)], 1)


def inc_data_hsv(model, hsv_columns):
    # Calculating distances
    dx, dy, dz = (np.arange(-PIXEL_AREA, PIXEL_AREA + 1) for _ in range(3))

    delta_columns = np.asarray(np.meshgrid(dx, dy, dz)).reshape((3, -1)).T
    dist_columns = np.sum(np.square(delta_columns), axis=1)

    delta_columns = delta_columns[dist_columns <= PIXEL_AREA**2]

    # Calculating resulting HSVs with offsets
    index_matrix = np.tile(
        delta_columns.flatten(),
        (hsv_columns.shape[0], 1),
    ) + np.tile(
        hsv_columns,
        delta_columns.shape[0],
    )
    index_matrix = np.reshape(index_matrix, (-1, 3)).astype('int64')

    # HSV filtering
    # Modulo of H
    index_matrix[:, 0] %= H_AMOUNT
    # Removing S and V out of borders
    index_matrix = index_matrix[
        np.logical_and(index_matrix[:, 1] >= 0, index_matrix[:, 1] < S_AMOUNT)
    ]
    index_matrix = index_matrix[
        np.logical_and(index_matrix[:, 2] >= 0, index_matrix[:, 2] < V_AMOUNT)
    ]

    index = (
        index_matrix[:, 0] * S_AMOUNT * V_AMOUNT
        + index_matrix[:, 1] * V_AMOUNT
        + index_matrix[:, 2]
    )

    np.add.at(model, index, 1)


def train_rgb(model_name):
    load_path = LOAD_PREFIX / model_name

    data_all = np.zeros(RGB_AMOUNT**3, dtype=TRAIN_DTYPE)
    data_object = np.zeros(RGB_AMOUNT**3, dtype=TRAIN_DTYPE)
    data_non_object = np.zeros(RGB_AMOUNT**3, dtype=TRAIN_DTYPE)

    for image_path in load_path.iterdir():
        if 'out' in image_path.name:
            continue

        time1 = time.time()

        image = load_image_rgba(image_path)

        r_layer, g_layer, b_layer = (
            np.asarray(image[:, :, i] // RGB_COMPRESSION) for i in range(3)
        )
        a_layer = image[:, :, 3]

        index_matrix = r_layer * RGB_AMOUNT**2 + g_layer * RGB_AMOUNT + b_layer

        inc_data_rgb(data_all, index_matrix, data_all.shape[0])
        inc_data_rgb(data_object, index_matrix[a_layer < 128], data_all.shape[0])
        inc_data_rgb(data_non_object, index_matrix[a_layer >= 128], data_all.shape[0])

        print(f'Image: {time.time() - time1}')

    np.save(get_model_path(model_name, model_id='obj'), data_object.reshape(MODEL_SHAPE))
    np.save(get_model_path(model_name, model_id='noobj'), data_non_object.reshape(MODEL_SHAPE))
    np.save(get_model_path(model_name, model_id='all'), data_all.reshape(MODEL_SHAPE))


def train_hsv(model_name):
    load_path = LOAD_PREFIX / model_name
    data_all = np.zeros(H_AMOUNT * S_AMOUNT * V_AMOUNT, dtype=TRAIN_DTYPE)
    data_object = np.zeros(H_AMOUNT * S_AMOUNT * V_AMOUNT, dtype=TRAIN_DTYPE)
    data_non_object = np.zeros(H_AMOUNT * S_AMOUNT * V_AMOUNT, dtype=TRAIN_DTYPE)

    for image_path in load_path.iterdir():
        if 'out' in image_path.name:
            continue

        time1 = time.time()

        rgba_image = load_image_rgba(image_path)
        a_layer = rgba_image[:, :, 3]

        hsv_data = np.reshape(rgba_to_hsv(rgba_image), (-1, 3))

        hsv_data[:, 0] //= H_COMPRESSION
        hsv_data[:, 1] //= S_COMPRESSION
        hsv_data[:, 2] //= V_COMPRESSION

        inc_data_hsv(data_all, hsv_data)
        inc_data_hsv(data_object, hsv_data[a_layer.flatten() < 128])
        inc_data_hsv(data_non_object, hsv_data[a_layer.flatten() >= 128])
        print(f'Image: {time.time() - time1}')

    np.save(get_model_path(model_name, model_id='obj'), data_object.reshape(MODEL_SHAPE))
    np.save(get_model_path(model_name, model_id='noobj'), data_non_object.reshape(MODEL_SHAPE))
    np.save(get_model_path(model_name, model_id='all'), data_all.reshape(MODEL_SHAPE))


def main():
    if len(sys.argv) < 2:
        print('Please specify at least one model for training.')
        sys.exit(1)

    for model_name in sys.argv[1:]:
        time1 = time.time()
        print(f'Training of {model_name} starts.')

        Path(get_model_path(model_name)).parent.mkdir(exist_ok=True)
        if COLOR_SCHEME == 'RGB':
            train_rgb(model_name)
        elif COLOR_SCHEME == 'HSV':
            train_hsv(model_name)

        print(f'Training success in {time.time() - time1}.')


if __name__ == '__main__':
    main()
