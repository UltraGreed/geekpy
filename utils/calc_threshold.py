import datetime
import os

from PIL import Image
import numpy as np

#####################
# CONFIG PARAMETERS #
THRESHOLD_COLOR = 75 ** 2
TARGET_COLOR = np.array([129, 179, 41])

THRESHOLD_IMAGE_PART = 0.1

CAMERA_FOV = 70
####################


# Function creating a bit mask of the image
def get_mask(pixel):
    error = np.sum(np.square(pixel - TARGET_COLOR))

    return True if error < THRESHOLD_COLOR else False


vec_get_mask = np.vectorize(get_mask, signature='(3)->()')


# Function creating a black and white array image of object
def get_bw(pixel):
    error = np.sum(np.square(pixel - TARGET_COLOR))

    return np.array([255, 255, 255]) if error < THRESHOLD_COLOR else np.array([0, 0, 0])


vec_get_bw = np.vectorize(get_bw, signature='(3)->(3)')


# Function saving black and white image with detected object for debugging
def save_bw_image(image, point_coords, save_path):
    image_bw_array = vec_get_bw(image)

    image_bw = Image.fromarray(image_bw_array.astype('uint8'))

    image_bw.putpixel(point_coords, (255, 0, 0))

    image_bw.save(save_path)


load_prefix = './photo/testing_recogn/chosen/'
save_prefix = './photo/recognized/'

for image_file in sorted(os.listdir(load_prefix)):
    image = Image.open(load_prefix + image_file)
    image_array = np.asarray(image)

    mask = vec_get_mask(image_array)

    y_coords, x_coords = mask.nonzero()

    if len(y_coords) >= THRESHOLD_IMAGE_PART * len(image_array):
        obj_x, obj_y = round(np.average(x_coords)), round(np.average(y_coords))

        # Saving black and white image with detected object for debugging
        timestamp = datetime.datetime.today().strftime("%Y%m%d_%H%M%S.%f")
        path = f"{save_prefix}/{image_file.replace('.jpg', '_bw.jpg')}"

        save_bw_image(image_array, (obj_x, obj_y), path)
        image.save(f'{save_prefix}/{image_file}')

        print('found')
    else:
        print('not found')
