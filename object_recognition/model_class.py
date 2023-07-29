import numpy as np

#####################
# CONFIG PARAMETERS #
# LOADING PARAMETERS #
MODEL_DIRECTORY = 'models/'
OBJ = "CellRdirt"
# OBJECT RECOGNITION PARAMETERS #
# Part of maximum image weight sum needed to recognize object
THRESHOLD_OBJECT = 0.001
# Part of maximum image weight sum to remove from image
THRESHOLD_CLEAN = 0.00001
# MODEL-WIDE PARAMETERS #
# Maximum possible value in model
MAX_PIXEL_WEIGHT = 1
# Dimensions of color space
COLOR_AMOUNT = 64
COLOR_COMPRESSION = 256 // COLOR_AMOUNT
# EDUCATION PARAMETERS #
# Area in which pixels incremented during learning
PIXEL_AREA = 2
# NORMALIZATION PARAMETERS #
# Thresholds for model normalization
UPPER_BORDER_OBJECT = 0.7
UPPER_BORDER_NON_OBJECT = 0.7
# Model value which will equal to zero chance
# Ranges from -1 to 1
LOWER_MODEL_BORDER = 0


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

        self._threshold_object = None
        self._threshold_clean = None

        self._image_center = None

        self._image_weight_raw = None
        self._image_weight = None
        self._image_sum = None

    @property
    def image(self):
        if self._image is not None:
            return self._image
        else:
            raise ImageNotLoaded

    @image.setter
    def image(self, value):
        self._image = value

        self._threshold_object = None
        self._threshold_clean = None

        self._image_center = None

        self._image_weight_raw = None
        self._image_weight = None
        self._image_sum = None

    @property
    def threshold_object(self):
        if self._threshold_object is None:
            self._threshold_object = THRESHOLD_OBJECT * len(self.image) ** 2 * MAX_PIXEL_WEIGHT

        return self._threshold_object

    @property
    def threshold_clean(self):
        if self._threshold_clean is None:
            self._threshold_clean = THRESHOLD_CLEAN * len(self.image) ** 2 * MAX_PIXEL_WEIGHT

        return self._threshold_clean

    @property
    def image_weight_raw(self):
        if self._image_weight_raw is None:
            r_layer, g_layer, b_layer = [
                np.asarray(
                    self.image[:, :, i] // COLOR_COMPRESSION, dtype='uint32'
                ) for i in range(3)
            ]

            index_matrix = np.asarray(r_layer * COLOR_AMOUNT ** 2 + g_layer * COLOR_AMOUNT + b_layer)

            self._image_weight_raw = self.model[index_matrix]

        return self._image_weight_raw

    @property
    def image_weight(self):
        if self._image_weight is None:
            # Removes low weighted areas of image
            # Arrays with sums of columns and rows
            col_sums = np.sum(self.image_weight_raw, axis=0)
            row_sums = np.sum(self.image_weight_raw, axis=1)
            # Starting indexes of iterators
            up = 0
            down = self.image.shape[0] - 1
            left = 0
            right = self.image.shape[1] - 1

            up_removed = 0
            down_removed = 0
            left_removed = 0
            right_removed = 0

            removed_sum = 0
            while removed_sum < self.threshold_clean and (up != down or left != right):
                min_weight = min(
                    row_sums[up] + up_removed,
                    row_sums[down] + down_removed,
                    col_sums[left] + left_removed,
                    col_sums[right] + right_removed
                )

                # Remove the lowest-sum side
                if up != down:
                    if left == right and min_weight in (col_sums[left] + left_removed, col_sums[right] + right_removed):
                        min_weight = min(row_sums[up] + up_removed, row_sums[down] + down_removed)

                    if min_weight == row_sums[up] + up_removed:
                        col_sums -= min_weight
                        up += 1
                        up_removed += min_weight
                    elif min_weight == row_sums[down] + down_removed:
                        col_sums -= min_weight
                        down -= 1
                        down_removed += min_weight

                if left != right:
                    if up == down and min_weight in (row_sums[up] + up_removed, row_sums[down] + down_removed):
                        min_weight = min(col_sums[left] + left_removed, col_sums[right] + right_removed)

                    if min_weight == col_sums[left] + left_removed:
                        row_sums -= min_weight
                        left += 1
                        left_removed += min_weight
                    elif min_weight == col_sums[right] + right_removed:
                        row_sums -= min_weight
                        right -= 1
                        right_removed += min_weight

                removed_sum += min_weight

            # Remaining part of image
            image_remain = self.image_weight_raw[up:down + 1, left:right + 1]

            # Pad resulting array to original size
            self._image_weight = np.pad(
                image_remain,
                ((up, self.image.shape[0] - down - 1),
                 (left, self.image.shape[1] - right - 1))
            )

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

    # Function returning boolean of object presence
    def check_object(self, new_image=None):
        if new_image is not None:
            self.image = new_image

        return self.image_sum >= self.threshold_object

    # Function creating a black and white array image of raw object
    def get_grayscale_raw(self):
        r_layer, g_layer = [
            np.where(np.asarray(self.image_weight_raw) == 0, 0, self.image_weight_raw * 255) for _ in range(2)
        ]
        b_layer = np.where(np.asarray(self.image_weight_raw) == 0, 255, self.image_weight_raw * 255)

        return np.dstack((np.asarray(layer, dtype='uint8') for layer in (r_layer, g_layer, b_layer)))

    # Function creating a black and white array image of object
    def get_grayscale(self):
        r_layer, g_layer = [
            np.where(np.asarray(self.image_weight) == 0, 0, self.image_weight * 255) for _ in range(2)
        ]
        b_layer = np.where(np.asarray(self.image_weight) == 0, 255, self.image_weight * 255)

        return np.dstack((np.asarray(layer, dtype='uint8') for layer in (r_layer, g_layer, b_layer)))
