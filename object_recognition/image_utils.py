import cv2
import numpy as np
import matplotlib.pyplot as plt


def load_image_rgba(path):
    img = cv2.imread(path, flags=-1)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    return np.asarray(img)


def save_image_rgba(path, img_array):
    img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
    cv2.imwrite(path, img)


