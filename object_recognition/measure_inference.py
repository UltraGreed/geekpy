import sys
import time

from image_utils import load_image_rgb

from model_class import RGBModel, HSVModel
from config import *
from model_class import get_model_path

from itertools import chain
from pathlib import Path


#####################
# CONFIG PARAMETERS #
obj_name = sys.argv[1]

LOAD_PATH = Path('images/selection_test/')
LOAD_OBJ = LOAD_PATH / obj_name
LOAD_POSITIVE_PATH = LOAD_OBJ / 'positive'
LOAD_NEGATIVE_PATH = LOAD_OBJ / 'negative'
####################


def check_image(image):
    time1 = time.time()
    model.check_object(image)
    print('Object inference done in', time.time() - time1)


if COLOR_SCHEME == 'RGB':
    model = RGBModel(get_model_path(obj_name))
elif COLOR_SCHEME == 'HSV':
    model = HSVModel(get_model_path(obj_name))

print('Image loading starts')
time1 = time.time()

image_files = chain(LOAD_POSITIVE_PATH.iterdir(), LOAD_NEGATIVE_PATH.iterdir())
images = [load_image_rgb(image_file) for image_file in image_files]

time2 = time.time()
for image in images:
    check_image(image)

print(f'{len(images)} images loaded in {time2 - time1}')
print(f'Inference done in {time.time() - time2}')
