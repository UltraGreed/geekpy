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

data_object_norm = data_object / object_max
data_non_object_norm = data_non_object / non_object_max

# Cut off the upper borders
data_object_norm = np.where(
    data_object_norm <= UPPER_BORDER_OBJECT,
    data_object_norm / UPPER_BORDER_OBJECT,
    1
)
data_non_object_norm = np.where(
    data_non_object_norm <= UPPER_BORDER_NON_OBJECT,
    data_non_object_norm / UPPER_BORDER_NON_OBJECT,
    1
)

np.save(get_model_path(obj_name, model_id='obj_norm'), data_object_norm)
np.save(get_model_path(obj_name, model_id='noobj_norm'), data_non_object_norm)

data_sub = data_object_norm - data_non_object_norm

# Normalize the subtraction model
data_sub_norm = np.where(
    data_sub >= LOWER_MODEL_BORDER,
    (data_sub - LOWER_MODEL_BORDER) / (1 - LOWER_MODEL_BORDER),
    0
)

np.save(get_model_path(obj_name, model_id='sub'), data_sub_norm)

print(f'Normalization success in {time.time() - time1}')
