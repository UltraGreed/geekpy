import sys
import time

import numpy as np

from model_class import get_model_path

from config import *

obj_name = sys.argv[1]

print('Normalization starts.')
time1 = time.time()

data_object = np.load(get_model_path(obj_name, model_id='obj'))
data_non_object = np.load(get_model_path(obj_name, model_id='noobj'))
data_all = np.load(get_model_path(obj_name, model_id='all'))

object_max = np.max(data_object)
non_object_max = np.max(data_non_object)

data_object_norm = (data_object * (MODEL_MAX_VALUE / object_max)).astype(MODEL_DTYPE)
data_non_object_norm = (data_non_object * (MODEL_MAX_VALUE / non_object_max)).astype(MODEL_DTYPE)

# Cut off the upper borders
data_object_norm[
    data_object_norm > UPPER_BORDER_OBJECT * MODEL_MAX_VALUE
] = UPPER_BORDER_OBJECT * MODEL_MAX_VALUE
data_object_norm = (data_object_norm / UPPER_BORDER_OBJECT).astype(MODEL_DTYPE)

data_non_object_norm[
    data_non_object_norm > UPPER_BORDER_OBJECT * MODEL_MAX_VALUE
] = UPPER_BORDER_OBJECT * MODEL_MAX_VALUE
data_non_object_norm = (data_non_object_norm / UPPER_BORDER_OBJECT).astype(MODEL_DTYPE)

np.save(get_model_path(obj_name, model_id='obj_norm'), data_object_norm)
np.save(get_model_path(obj_name, model_id='noobj_norm'), data_non_object_norm)

data_sub = data_object_norm.astype(np.int64) - data_non_object_norm

# Normalize the subtraction model
data_sub_norm = (np.where(
    data_sub > LOWER_MODEL_BORDER * MODEL_MAX_VALUE,
    data_sub - LOWER_MODEL_BORDER * MODEL_MAX_VALUE,
    0,
) / (1 - LOWER_MODEL_BORDER)).astype(MODEL_DTYPE)

np.save(get_model_path(obj_name, model_id='sub'), data_sub_norm)

print(f'Normalization success in {time.time() - time1}')
