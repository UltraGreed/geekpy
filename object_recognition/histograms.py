import sys

import numpy as np
from image_utils import save_image_rgb
from model_class import get_model_path
from config import *


obj_name = sys.argv[1]


def get_histogram_separate(axel_ind):
    image_g = np.zeros(MODEL_SHAPE[:axel_ind] + MODEL_SHAPE[axel_ind + 1:], dtype='uint8')

    image_r = np.max(data_obj_norm, axis=axel_ind) // MODEL_IMAGE_CAST
    image_b = np.max(data_non_obj_norm, axis=axel_ind) // MODEL_IMAGE_CAST

    return np.stack(
        (image_r.astype(np.uint8),
         image_g.astype(np.uint8),
         image_b.astype(np.uint8)),
        axis=-1,
    )


def get_histogram_model(axel_ind):
    image_g = np.zeros(MODEL_SHAPE[:axel_ind] + MODEL_SHAPE[axel_ind + 1:], dtype='uint8')

    image_r = np.max(data_sub, axis=axel_ind) // MODEL_IMAGE_CAST

    image_b = np.where(
        np.max(data_sub, axis=axel_ind) == 0,
        np.asarray(255, dtype=np.uint8),
        np.asarray(0, dtype=np.uint8),
    )

    return np.stack(
        (image_r.astype(np.uint8),
         image_g.astype(np.uint8),
         image_b.astype(np.uint8)),
        axis=-1,
    )


data_obj_norm = np.load(get_model_path(obj_name, 'obj_norm')).reshape(MODEL_SHAPE)
data_non_obj_norm = np.load(get_model_path(obj_name, 'noobj_norm')).reshape(MODEL_SHAPE)
data_sub = np.load(get_model_path(obj_name, 'sub')).reshape(MODEL_SHAPE)

save_image_rgb('hist_sep_SV.png', get_histogram_separate(0))
save_image_rgb('hist_sep_HV.png', get_histogram_separate(1))
save_image_rgb('hist_sep_HS.png', get_histogram_separate(2))

save_image_rgb('hist_model_SV.png', get_histogram_model(0))
save_image_rgb('hist_model_HV.png', get_histogram_model(1))
save_image_rgb('hist_model_HS.png', get_histogram_model(2))
