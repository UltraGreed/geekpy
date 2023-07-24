import numpy as np

#####################
# CONFIG PARAMETERS #
THRESHOLD_IMAGE_PART = 0.1

THRESHOLD_MIN = 0.99
THRESHOLD_MAX = 0.999

COLOR_AMOUNT = 64
COLOR_COMPRESSION = 256 / COLOR_AMOUNT

PATH_TO_MODEL = 'model_divided.npy'
####################


class Model:
    def __init__(self):
        self.model = np.load(PATH_TO_MODEL)

        self.model_max = np.max(self.model)
        self.model_min = np.min(self.model)

        self.model_lower_border = self.model_min + THRESHOLD_MIN * (self.model_max - self.model_min)
        self.model_upper_border = self.model_min + THRESHOLD_MAX * (self.model_max - self.model_min)

        self.get_mask = np.vectorize(self.get_mask_pixel, signature='(n)->()')
        self.get_grayscale = np.vectorize(self.get_gray_pixel, signature='(n)->(n)')

    def get_model_data(self, pixel):
        x, y, z = [int(i // COLOR_COMPRESSION) for i in [
            pixel[0],
            pixel[1],
            pixel[2]
        ]]
        return self.model[x][y][z]

    # Function creating a bit mask of the image
    def get_mask_pixel(self, pixel):
        return self.get_model_data(pixel) >= self.model_upper_border

    # Function creating a black and white array image of object
    def get_gray_pixel(self, pixel):
        value = self.get_model_data(pixel)

        if value < self.model_lower_border:
            alpha = 0
        elif value >= self.model_upper_border:
            alpha = 255
        else:
            alpha = 255 * (value - self.model_lower_border) / (self.model_upper_border - self.model_lower_border)

        gray_pixel = np.asarray([0, 255, 0, alpha], dtype='uint8')

        return gray_pixel


