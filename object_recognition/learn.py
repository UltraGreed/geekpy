import datetime
import os
import time

import numpy as np

from image_utils import load_image_rgba, save_image_rgba

#####################
# CONFIG PARAMETERS #
PIXEL_AREA = 1

COLOR_AMOUNT = 64
COLOR_COMPRESSION = 256 / COLOR_AMOUNT
#####################


def get_bw(pixel):
    return pixel if pixel[3] == 0 else np.asarray([255, 255, 255, 255], dtype='uint8')


vec_get_bw = np.vectorize(get_bw, signature='(n)->(n)')

data_found = np.zeros(tuple(COLOR_AMOUNT for _ in range(3)))
data_not_found = np.zeros(tuple(COLOR_AMOUNT for _ in range(3)))
data_all = np.zeros(tuple(COLOR_AMOUNT for _ in range(3)))

load_prefix = 'images/selection_learn/'
save_prefix = 'images/selection_learn/'

for image_file in os.listdir(load_prefix):
    if not image_file.startswith('learning') or 'out' in image_file:
        continue

    time1 = time.time()
    image_array = load_image_rgba(load_prefix + image_file)
    print(f"Image loaded: {time.time() - time1}")

    time2 = time.time()
    for row in image_array:
        for pixel in row:
            x, y, z = [int(i // COLOR_COMPRESSION + 0.5) for i in pixel[:3]]
            data_all[x][y][z] += 1
            if pixel[3] == 0:
                data_found[x][y][z] += 1
            else:
                data_not_found[x][y][z] += 1

    print(f"Image processed: {time.time() - time2}")

    time3 = time.time()
    image_bw_array = vec_get_bw(image_array)
    print(f'Image bw generated: {time.time() - time3}')

    time4 = time.time()
    save_image_rgba(load_prefix + image_file.replace('.png', '_out.png'), image_bw_array)
    print(f"Image saved: {time.time() - time4}")

    print(f"Total: {time.time() - time1}")


np.save('model_found.npy', data_found)
np.save('model_not_found.npy', data_not_found)
np.save('model_all.npy', data_all)

np.save('model_divided.npy', data_found / np.where(data_all > 0, data_all, 1))