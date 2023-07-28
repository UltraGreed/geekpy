import numpy as np


#####################
# CONFIG PARAMETERS #
# LOADING PARAMETERS
MODEL_DIRECTORY = 'models/'
OBJ = "BallY"
# OBJECT RECOGNITION PARAMETERS
THRESHOLD_IMAGE_PART = 0.001
# MODEL-WIDE PARAMETERS
# Maximum possible value in model
MAX_PIXEL_WEIGHT = 1
# Dimensions of color space
COLOR_AMOUNT = 64
COLOR_COMPRESSION = 256 // COLOR_AMOUNT
# EDUCATION PARAMETERS
# Area in which pixels incremented during learning
PIXEL_AREA = 2
# NORMALIZATION PARAMETERS
# Thresholds for model normalization
UPPER_BORDER_OBJECT = 0.7
UPPER_BORDER_NON_OBJECT = 0.7
# Model value which will equal to zero chance
# Ranges from -1 to 1
LOWER_SUB_MODEL_BORDER = 0
####################


def get_model_learn_path(model_id):
    return MODEL_DIRECTORY + f'{model_id}_{OBJ}_{COLOR_AMOUNT}.npy'


def get_model_inference_path(model_id, obj_name):
    return MODEL_DIRECTORY + f'{model_id}_{obj_name}_{COLOR_AMOUNT}.npy'


class ImageNotLoaded(Exception):
    pass


class Model:
    def __init__(self, model_path):
        self.model = np.load(model_path)

        self.model_max = np.max(self.model)
        self.model_min = np.min(self.model)

        self._image = None
        self._mask = None
        self._threshold_weight = None
        self._image_sum = None
        self._image_center = None
        self._image_weight = None


    # Function creating a black and white array image of object
    def get_grayscale(self):
        r_layer, g_layer, b_layer = [np.asarray(self.image_weight * 255, dtype='uint8') for _ in range(3)]

        return np.dstack((r_layer, g_layer, b_layer))

    @property
    def image(self):
        if self._image is not None:
            return self._image
        else:
            raise ImageNotLoaded

    @image.setter
    def image(self, value):
        self._image = value
        self._mask = None
        self._threshold_weight = None
        self._image_sum = None
        self._image_center = None
        self._image_weight = None

    @property
    def threshold_weight(self):
        if self._threshold_weight is None:
            self._threshold_weight = THRESHOLD_IMAGE_PART * len(self.image) ** 2 * MAX_PIXEL_WEIGHT

        return self._threshold_weight

    @property
    def image_weight(self):
        if self._image_weight is None:
            r_layer, g_layer, b_layer = [
                np.asarray(
                    self.image[:, :, i] // COLOR_COMPRESSION, dtype='uint32'
                ) for i in range(3)
            ]

            index_matrix = np.asarray(r_layer * COLOR_AMOUNT ** 2 + g_layer * COLOR_AMOUNT + b_layer)

            self._image_weight = self.model[index_matrix]

        return self._image_weight

    @property
    def image_sum(self):
        if self._image_sum is None:
            self._image_sum = np.sum(self.image_weight)

        return self._image_sum

    @property
    def object_center(self):
        if not self.check_object():
            return 0, 0
        if self._image_center is None:
            mean_x = np.dot(np.arange(0, self.image.shape[0]), np.sum(self.image_weight, axis=1)) / self.image_sum
            mean_y = np.dot(np.arange(0, self.image.shape[1]), np.sum(self.image_weight, axis=0)) / self.image_sum
            self._image_center = np.asarray([mean_x, mean_y])

        return self._image_center

    def check_object(self, new_image=None):
        if new_image is not None:
            self.image = new_image

        return self.image_sum >= self.threshold_weight
