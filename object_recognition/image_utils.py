import cv2
import numpy as np


def load_image(path: str, color_convert: int):
    img = cv2.imread(path, flags=-1)
    img = cv2.cvtColor(img, color_convert)
    return np.asarray(img, dtype='float64')


def save_image(path: str, img_array: np.ndarray, color_convert: int):
    img = cv2.cvtColor(np.asarray(img_array, dtype='uint8'), color_convert)
    cv2.imwrite(path, img)


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