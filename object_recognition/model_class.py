import numpy as np

#####################
# CONFIG PARAMETERS #
THRESHOLD_IMAGE_PART = 0.01

THRESHOLD_MIN = 0.0
THRESHOLD_MAX = 1.0

COLOR_AMOUNT = 2
COLOR_COMPRESSION = 256 // COLOR_AMOUNT

MAX_PIXEL_WEIGHT = 1

OBJ = "CellRdirt"
####################


class ImageNotLoaded(Exception):
    pass


class Model:
    def __init__(self, model_path):
        self.model = np.load(model_path)

        self.model_max = np.max(self.model)
        self.model_min = np.min(self.model)

        self.model_lower_border = self.model_min + THRESHOLD_MIN * (self.model_max - self.model_min)
        self.model_upper_border = self.model_min + THRESHOLD_MAX * (self.model_max - self.model_min)

        self._image = None
        self._mask = None
        self._threshold_weight = None
        self._image_sum = None
        self._image_center = None
        self._image_weight = None

    def get_pixel_raw(self, index):
        return self.model[index]

    def get_pixel_weight(self, index):
        pixel_data = self.get_pixel_raw(index)

        """
        Sorry for some unreadable code, IDK if it can be done better with np.
        Brief explanation:
        we want to cut lower and upper borders from model,
        so we make everything below lower border equal to 0
        and everything above upper border equal to 1
        then we make everything between lower and upper borders equal to proportion of value 
        between borders: (value - lower border) / (upper border - lower border)
        """
        pixel_weight = np.where(pixel_data < self.model_lower_border, 0, pixel_data)
        pixel_weight = np.where(pixel_weight >= self.model_upper_border, 1, pixel_weight)
        pixel_weight = np.where(
            np.logical_and(pixel_weight >= self.model_lower_border, pixel_weight < self.model_upper_border),
            (pixel_weight - self.model_lower_border) / (self.model_upper_border - self.model_lower_border),
            pixel_weight
        )
        return pixel_weight

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

            self._image_weight = self.get_pixel_weight(index_matrix)

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
