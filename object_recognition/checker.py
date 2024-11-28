import sys
import time
from pathlib import Path

from image_utils import load_image_rgb, save_image_rgb

from model_class import RGBModel, HSVModel
from config import *
from model_class import get_model_path


#####################
# CONFIG PARAMETERS #
obj_name = sys.argv[1]

LOAD_PATH = Path('images/selection_test/')
LOAD_OBJ = LOAD_PATH / obj_name
LOAD_POSITIVE_PATH = LOAD_OBJ / 'positive'
LOAD_NEGATIVE_PATH = LOAD_OBJ / 'negative'

ENABLE_OUTPUT = True

SAVE_PATH = Path('images/result_test/')
SAVE_TRUE_POSITIVE_PATH = SAVE_PATH / 'true_positive'
SAVE_FALSE_POSITIVE_PATH = SAVE_PATH / 'false_positive'
SAVE_TRUE_NEGATIVE_PATH = SAVE_PATH / 'true_negative'
SAVE_FALSE_NEGATIVE_PATH = SAVE_PATH / 'false_negative'
####################


def clear_dir(path):
    files = path.glob('*')
    for file in files:
        file.unlink()


def load_check_image(image_path, is_obj):
    time1 = time.time()
    image = load_image_rgb(image_path)

    time2 = time.time()
    is_obj_found = model.check_object(image)
    print('Object inference done in', time.time() - time2)

    is_correct = is_obj == is_obj_found
    if is_correct and is_obj:
        save_path = SAVE_TRUE_POSITIVE_PATH
        result = 'Found true positive '
    elif not is_correct and is_obj:
        save_path = SAVE_FALSE_POSITIVE_PATH
        result = 'Found false positive '
    elif is_correct and not is_obj:
        save_path = SAVE_TRUE_NEGATIVE_PATH
        result = 'Found true negative '
    else:
        save_path = SAVE_FALSE_NEGATIVE_PATH
        result = 'Found false negative '

    print(result + image_path.name) # type: ignore

    # Copying original image according to our model
    original_path = save_path / image_path.name # type: ignore
    save_image_rgb(original_path, image)

    # Saving image mask with detected object for debugging
    image_debug = model.get_debug()
    debug_path = save_path / (image_path.stem + '_mask' + image_path.suffix) # type: ignore
    save_image_rgb(debug_path, image_debug)

    print('Image checked in ', time.time() - time1)
    return is_correct


LOAD_POSITIVE_PATH.mkdir(parents=True, exist_ok=True)
LOAD_NEGATIVE_PATH.mkdir(parents=True, exist_ok=True)

for directory in (
    SAVE_TRUE_NEGATIVE_PATH,
    SAVE_FALSE_NEGATIVE_PATH,
    SAVE_TRUE_POSITIVE_PATH,
    SAVE_FALSE_POSITIVE_PATH,
):
    directory.mkdir(parents=True, exist_ok=True)
    clear_dir(directory)

if COLOR_SCHEME == 'RGB':
    model = RGBModel(get_model_path(obj_name))
elif COLOR_SCHEME == 'HSV':
    model = HSVModel(get_model_path(obj_name))

print('Checker starts')
time1 = time.time()
true_positive, true_negative = 0, 0
for image_path in LOAD_POSITIVE_PATH.iterdir():
    if load_check_image(image_path, is_obj=True):
        true_positive += 1

for image_path in LOAD_NEGATIVE_PATH.iterdir():
    if load_check_image(image_path, is_obj=False):
        true_negative += 1

print(f'Checker success in {time.time() - time1}')
print(f'True positive: {true_positive}/{len(list(LOAD_POSITIVE_PATH.iterdir()))}')
print(f'True negative: {true_negative}/{len(list(LOAD_NEGATIVE_PATH.iterdir()))}')
