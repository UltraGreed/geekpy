import numpy as np

#####################
# CONFIG PARAMETERS #
THRESHOLD_IMAGE_PART = 0.001

THRESHOLD_MIN = 0.01
THRESHOLD_MAX = 0.9

COLOR_AMOUNT = 16
COLOR_COMPRESSION = 256 / COLOR_AMOUNT

MAX_PIXEL_WEIGHT = 1
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

        self.get_mask = np.vectorize(self.get_mask_pixel, signature='(n)->()')
        self.get_grayscale = np.vectorize(self.get_gray_pixel, signature='(n)->(4)')
        self.calc_image_weight = np.vectorize(self.get_pixel_weight, signature='(n)->()')

        self._image = None
        self._mask = None
        self._threshold_pixel = None
        self._image_sum = None
        self._image_center = None
        self._image_weight = None

    def get_pixel_raw(self, pixel):
        x, y, z = [int(i // COLOR_COMPRESSION) for i in [
            pixel[0],
            pixel[1],
            pixel[2]
        ]]
        return self.model[x][y][z]

    def get_pixel_weight(self, pixel):
        pixel_data = self.get_pixel_raw(pixel)

        if pixel_data < self.model_lower_border:
            pixel_weight = 0
        elif pixel_data >= self.model_upper_border:
            pixel_weight = 255
        else:
            pixel_weight = 255 * (pixel_data - self.model_lower_border) / (self.model_upper_border - self.model_lower_border)

        return pixel_weight

    # Function creating a bit mask of the image
    def get_mask_pixel(self, pixel):
        return self.get_pixel_raw(pixel) >= self.model_upper_border

    # Function creating a black and white array image of object
    def get_gray_pixel(self, pixel):
        value = self.get_pixel_weight(pixel)

        gray_pixel = np.asarray([value * 255, value * 255, value * 255, 255], dtype='uint8')

        return gray_pixel

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
        self._threshold_pixel = None
        self._image_sum = None
        self._image_center = None
        self._image_weight = None

    @property
    def mask(self):
        if self._image is None:
            raise ImageNotLoaded
        if self._mask is None:
            self._mask = self.get_mask(self._image)
        return self._mask

    @property
    def threshold_pixel(self):
        if self._threshold_pixel is None:
            self._threshold_pixel = THRESHOLD_IMAGE_PART * len(self.image) ** 2

        return self._threshold_pixel

    @property
    def image_weight(self):
        if self._image_weight is None:
            self._image_weight = self.calc_image_weight(self.image)

        return self._image_weight

    @property
    def image_sum(self):
        if self._image_sum is None:
            self._image_sum = np.sum(self.image_weight)

        return self._image_sum

    @property
    def object_center(self):
        if self._image_center is None:
            mean_x = np.dot(np.arange(0, self.image.shape[0]), np.sum(self.image_weight, axis=1)) / self.image_sum
            mean_y = np.dot(np.arange(0, self.image.shape[1]), np.sum(self.image_weight, axis=0)) / self.image_sum
            self._image_center = np.asarray([mean_x, mean_y])

        return self._image_center

    def check_object(self, new_image=None):
        if new_image is not None:
            self.image = new_image

        return self.image_sum >= THRESHOLD_IMAGE_PART
