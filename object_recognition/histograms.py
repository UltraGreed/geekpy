import numpy as np
from image_utils import save_image_rgba
from model_class import COLOR_AMOUNT
from model_class import get_model_path


def get_histogram_image(axel_ind):
    image_r = np.zeros((COLOR_AMOUNT, COLOR_AMOUNT), dtype='uint8')
    image_g = np.zeros((COLOR_AMOUNT, COLOR_AMOUNT), dtype='uint8')
    image_b = np.zeros((COLOR_AMOUNT, COLOR_AMOUNT), dtype='uint8')
    image_a = np.full((COLOR_AMOUNT, COLOR_AMOUNT), 255, dtype='uint8')

    for i in range(image_r.shape[0]):
        for j in range(image_r.shape[1]):
            if axel_ind == 0:
                image_b[i][j] = np.round(np.max(data_non_object_norm[:, i, j]) * 255)
                image_r[i][j] = np.round(np.max(data_obj_norm[:, i, j]) * 255)
            elif axel_ind == 1:
                image_b[i][j] = np.round(np.max(data_non_object_norm[i, :, j]) * 255)
                image_r[i][j] = np.round(np.max(data_obj_norm[i, :, j]) * 255)
            elif axel_ind == 2:
                image_b[i][j] = np.round(np.max(data_non_object_norm[i, j, :]) * 255)
                image_r[i][j] = np.round(np.max(data_obj_norm[i, j, :]) * 255)

    return np.stack((image_r, image_g, image_b, image_a), axis=-1)


data_obj_norm = np.load(get_model_path('obj_norm')).reshape((COLOR_AMOUNT, COLOR_AMOUNT, COLOR_AMOUNT))
data_non_object_norm = np.load(get_model_path('noobj_norm')).reshape((COLOR_AMOUNT, COLOR_AMOUNT, COLOR_AMOUNT))

save_image_rgba('hist_gb.png', get_histogram_image(0))
save_image_rgba('hist_rb.png', get_histogram_image(1))
save_image_rgba('hist_rg.png', get_histogram_image(2))
