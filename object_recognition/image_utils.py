import cv2
import numpy as np

import math
from pathlib import Path


def load_image(path: str, color_convert: int = None):
    img = cv2.imread(str(path), flags=-1)
    if color_convert is not None:
        img = cv2.cvtColor(img, color_convert)
    return img


def save_image(path: str, img_array: np.ndarray, color_convert: int):
    img = cv2.cvtColor(img_array, color_convert)
    cv2.imwrite(str(path), img)


def load_image_gray(path):
    return load_image(path)


def save_image_gray(path: str, img_array: np.ndarray):
    save_image(path, img_array, cv2.COLOR_GRAY2BGR)


def load_image_rgba(path):
    return load_image(path, cv2.COLOR_BGRA2RGBA)


def save_image_rgba(path, img_array):
    save_image(path, img_array, cv2.COLOR_RGBA2BGRA)


def load_image_rgb(path):
    return load_image(path, cv2.COLOR_BGR2RGB)


def save_image_rgb(path, img_array):
    save_image(path, img_array, cv2.COLOR_RGB2BGR)


def load_image_hsv(path):
    return load_image(path, cv2.COLOR_BGR2HSV)


def save_image_hsv(path, img_array):
    save_image(path, img_array, cv2.COLOR_HSV2BGR)


def rgba_to_hsv(img_array):
    return cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2HSV)


def rgb_to_hsv(img_array):
    return cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)


def crop(img_array, new_shape):
    if new_shape[0] < img_array.shape[0]:
        crop_index = (img_array.shape[0] - new_shape[0]) // 2
        img_array = img_array[crop_index:img_array.shape[0] - 1 - crop_index]
    if new_shape[1] < img_array.shape[1]:
        crop_index = (img_array.shape[1] - new_shape[1]) // 2
        img_array = img_array[:, crop_index:img_array.shape[1] - 1 - crop_index]

    return img_array


# Calculate how big should be image to contain given space in real world
def meters_to_pixels(meters, distance, fov, image_side):
    return image_side * meters / distance / (2 * math.tan(fov / 2))
