import datetime
import os

import numpy as np

from image_utils import load_image_rgba, save_image_rgba

#####################
# CONFIG PARAMETERS #
PIXEL_AREA = 0

COLOR_AMOUNT = 64
COLOR_COMPRESSION = 256 / COLOR_AMOUNT
#####################


# Function creating a bit mask of the image
def get_mask(pixel):
    return True if pixel[3] != 255 else False


vec_get_mask = np.vectorize(get_mask, signature='(3)->()')


def get_bw(pixel):
    return pixel if pixel[3] == 0 else np.array([255, 255, 255, 255], dtype='uint8')


vec_get_bw = np.vectorize(get_bw, signature='(n)->(n)')

data = np.zeros((256, 256, 256))

load_prefix = 'images/selection_learn/'
save_prefix = 'images/selection_learn/'

for image_file in os.listdir(load_prefix):
    if not image_file.startswith('learning') or 'out' in image_file:
        continue

    image_array = load_image_rgba(load_prefix + image_file)

    for row in image_array:
        for pixel in row:
            if pixel[3] == 0:
                change = 1
            else:
                change = -1

            for off_x in range(-PIXEL_AREA, PIXEL_AREA + 1):
                for off_y in range(-PIXEL_AREA, PIXEL_AREA + 1):
                    for off_z in range(-PIXEL_AREA, PIXEL_AREA + 1):
                        if any([i > 255 or i < 0 for i in (pixel[0] + off_x, pixel[1] + off_y, pixel[2] + off_z)]):
                            continue

                        x, y, z = [round(i / COLOR_COMPRESSION) for i in [
                            pixel[0] + off_x,
                            pixel[1] + off_y,
                            pixel[2] + off_z
                        ]]
                        data[x][y][z] += change

    image_bw_array = vec_get_bw(image_array)

    save_image_rgba(load_prefix + image_file.replace('.png', '_out.png'), image_bw_array)

    print('image processed')

np.save('model.npy', data)
