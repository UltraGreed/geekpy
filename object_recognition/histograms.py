import numpy as np
from image_utils import save_image_rgba


data_found = np.load('model_found.npy')
data_not_found = np.load('model_not_found.npy')

max_all = np.max(data_not_found)
max_found = np.max(data_found)

image_r = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_g = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_b = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_a = np.full((data_not_found.shape[0], data_not_found.shape[1]), 255, dtype='uint8')

for i in range(image_r.shape[0]):
    for j in range(image_r.shape[1]):
        image_b[i][j] = np.round(np.max(data_not_found[i, j, :]) / max_all * 255)
        image_r[i][j] = np.round(np.max(data_found[i, j, :]) / max_found * 255)

hist_rg = np.stack((image_r, image_g, image_b, image_a), axis=-1)

save_image_rgba('hist_rg.png', hist_rg)

image_r = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_g = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_b = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_a = np.full((data_not_found.shape[0], data_not_found.shape[1]), 255, dtype='uint8')

for i in range(image_r.shape[0]):
    for j in range(image_r.shape[1]):
        image_b[i][j] = np.round(np.max(data_not_found[i, :, j]) / max_all * 255)
        image_r[i][j] = np.round(np.max(data_found[i, :, j]) / max_found * 255)

hist_rb = np.stack((image_r, image_g, image_b, image_a), axis=-1)

save_image_rgba('hist_rb.png', hist_rb)

image_r = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_g = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_b = np.zeros((data_not_found.shape[0], data_not_found.shape[1]), dtype='uint8')
image_a = np.full((data_not_found.shape[0], data_not_found.shape[1]), 255, dtype='uint8')

for i in range(image_r.shape[0]):
    for j in range(image_r.shape[1]):
        image_b[i][j] = np.round(np.max(data_not_found[:, i, j]) / max_all * 255)
        image_r[i][j] = np.round(np.max(data_found[:, i, j]) / max_found * 255)

hist_gb = np.stack((image_r, image_g, image_b, image_a), axis=-1)

save_image_rgba('hist_gb.png', hist_gb)
