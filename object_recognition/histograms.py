import numpy as np
from image_utils import save_image_rgba
from model_class import COLOR_AMOUNT
from model_class import get_model_learn_path


def get_histogram_separate(axel_ind):
    image_g = np.zeros((COLOR_AMOUNT, COLOR_AMOUNT), dtype='uint8')
    image_a = np.full((COLOR_AMOUNT, COLOR_AMOUNT), 255, dtype='uint8')

    image_b = np.round(np.max(data_non_obj_norm, axis=axel_ind) * 255)
    image_r = np.round(np.max(data_obj_norm, axis=axel_ind) * 255)

    return np.stack((image_r.astype('uint8'), image_g, image_b.astype('uint8'), image_a), axis=-1)


def get_histogram_model(axel_ind):
    image_g = np.zeros((COLOR_AMOUNT, COLOR_AMOUNT), dtype='uint8')
    image_a = np.full((COLOR_AMOUNT, COLOR_AMOUNT), 255, dtype='uint8')

    image_b = np.where(np.max(data_sub, axis=axel_ind) == 0, 255, 0)
    image_r = np.round(np.max(data_sub, axis=axel_ind) * 255)

    return np.stack((image_r.astype('uint8'), image_g, image_b.astype('uint8'), image_a), axis=-1)


data_obj_norm = np.load(get_model_learn_path('obj_norm')).reshape((COLOR_AMOUNT, COLOR_AMOUNT, COLOR_AMOUNT))
data_non_obj_norm = np.load(get_model_learn_path('noobj_norm')).reshape((COLOR_AMOUNT, COLOR_AMOUNT, COLOR_AMOUNT))
data_sub = np.load(get_model_learn_path('sub')).reshape((COLOR_AMOUNT, COLOR_AMOUNT, COLOR_AMOUNT))

save_image_rgba('hist_sep_gb.png', get_histogram_separate(0))
save_image_rgba('hist_sep_rb.png', get_histogram_separate(1))
save_image_rgba('hist_sep_rg.png', get_histogram_separate(2))

save_image_rgba('hist_model_gb.png', get_histogram_model(0))
save_image_rgba('hist_model_rb.png', get_histogram_model(1))
save_image_rgba('hist_model_rg.png', get_histogram_model(2))