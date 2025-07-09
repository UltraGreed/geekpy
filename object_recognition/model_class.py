import numpy as np

from object_recognition.config import (
    COLOR_SCHEME,
    H_COMPRESSION,
    MODEL_DIRECTORY,
    MODEL_IMAGE_CAST,
    MODEL_MAX_VALUE,
    MODEL_NEXT_DTYPE,
    MODEL_NEXT_SIGNED_DTYPE,
    PIXEL_SIZE_COEFFICIENT,
    RGB_COMPRESSION,
    S_COMPRESSION,
    THRESHOLD_CLEAN,
    THRESHOLD_OBJECT,
    V_COMPRESSION,
)
from object_recognition.image_utils import rgb_to_hsv

from pathlib import Path


def get_model_path(
    obj_name, model_id='sub', color_scheme=COLOR_SCHEME, model_dir_path=MODEL_DIRECTORY
):
    return Path(model_dir_path) / f'{model_id}_{obj_name}_{color_scheme.upper()}.npy'


def create_inference_model(
    obj_name, model_id='sub', color_scheme=COLOR_SCHEME, model_dir_path=MODEL_DIRECTORY, **kwargs
):
    """Create inference model for provided object. All **kwargs go to model class."""
    if color_scheme == 'HSV':
        model_class = HSVModel
    elif color_scheme == 'RGB':
        model_class = RGBModel
    else:
        raise NotImplementedError

    model_path = get_model_path(
        obj_name,
        model_id=model_id,
        color_scheme=color_scheme,
        model_dir_path=model_dir_path,
    )

    return model_class(model_path, **kwargs)


class ImageNotLoadedError(Exception):
    pass


class InferenceModel:
    def __init__(
        self,
        get_image_weight,
        threshold_object_part=THRESHOLD_OBJECT,
        threshold_clean_part=THRESHOLD_CLEAN,
    ):
        self.get_image_weight = get_image_weight

        self._image = None

        self._threshold_object_part = threshold_object_part
        self._threshold_clean_part = threshold_clean_part

        self._threshold_object = None
        self._threshold_clean = None

        self._object_center = None
        self._object_dispersion_sq = None
        self._object_pixel_size = None

        self._image_weight_raw = None
        self._image_weight = None
        self._image_sum = None

    @property
    def image(self):
        if self._image is not None:
            return self._image

        raise ImageNotLoadedError

    @image.setter
    def image(self, value):
        self._image = value

        self._threshold_object = None
        self._threshold_clean = None

        self._object_center = None
        self._object_dispersion_sq = None
        self._object_pixel_size = None

        self._image_weight_raw = None
        self._image_weight = None
        self._image_sum = None

    @property
    def threshold_object(self):
        if self._threshold_object is None:
            self._threshold_object = (
                self._threshold_object_part * len(self.image) ** 2 * MODEL_MAX_VALUE
            )

        return self._threshold_object

    @property
    def threshold_clean(self):
        if self._threshold_clean is None:
            self._threshold_clean = (
                self._threshold_clean_part * len(self.image) ** 2 * MODEL_MAX_VALUE
            )

        return self._threshold_clean

    @property
    def image_weight_raw(self):
        if self._image_weight_raw is None:
            self._image_weight_raw = self.get_image_weight(self.image)

        return self._image_weight_raw

    @property
    def image_weight(self):
        if self._image_weight is None:
            # Removes low weighted borders of image
            # Arrays with sums of columns and rows
            col_sums = np.sum(self.image_weight_raw, axis=0, dtype=MODEL_NEXT_DTYPE)
            row_sums = np.sum(self.image_weight_raw, axis=1, dtype=MODEL_NEXT_DTYPE)
            # Starting indexes of iterators
            up = 0
            down = self.image.shape[0] - 1
            left = 0
            right = self.image.shape[1] - 1

            up_removed = 0
            down_removed = 0
            left_removed = 0
            right_removed = 0

            while (
                (up_removed <= self.threshold_clean / 4 or down_removed <= self.threshold_clean / 4)
                and up != down
                or (
                    left_removed <= self.threshold_clean / 4
                    or right_removed <= self.threshold_clean / 4
                )
                and left != right
            ):
                if up_removed <= self.threshold_clean / 4 and up != down:
                    up += 1
                    up_removed += row_sums[up]
                if down_removed <= self.threshold_clean / 4 and up != down:
                    down -= 1
                    down_removed += row_sums[down]
                if left_removed <= self.threshold_clean / 4 and left != right:
                    left += 1
                    left_removed += col_sums[left]
                if right_removed <= self.threshold_clean / 4 and left != right:
                    right -= 1
                    right_removed += col_sums[right]

            # Remaining part of image
            image_remain = self.image_weight_raw[up : down + 1, left : right + 1]

            # Pad resulting array to original size
            self._image_weight = np.pad(
                image_remain,
                ((up, self.image.shape[0] - down - 1), (left, self.image.shape[1] - right - 1)),
            )

        return self._image_weight

    @property
    def image_sum(self):
        if self._image_sum is None:
            self._image_sum = np.sum(self.image_weight, dtype=MODEL_NEXT_DTYPE)

        return self._image_sum

    @property
    def object_center(self):
        if self.image_sum == 0:
            return self.image.shape[0] // 2, self.image.shape[1] // 2
        if self._object_center is None:
            mean_y = np.dot(
                np.arange(0, self.image.shape[0]),
                np.sum(self.image_weight, axis=1, dtype=MODEL_NEXT_DTYPE),
            ) / self.image_sum
            mean_x = np.dot(
                np.arange(0, self.image.shape[1]),
                np.sum(self.image_weight, axis=0, dtype=MODEL_NEXT_DTYPE),
            ) / self.image_sum
            self._object_center = (float(mean_y), float(mean_x))

        return self._object_center

    @property
    # HACK: Potential bottleneck here
    def object_dispersion_sq(self):
        if self._object_dispersion_sq is None:
            dispersion_x = np.sum(
                np.tile(
                    np.arange(0, self.image.shape[0], dtype=MODEL_NEXT_SIGNED_DTYPE)[:, np.newaxis]
                    - self.object_center[0],
                    (1, self.image.shape[1]),
                )
                ** 2
                * self.image_weight,
                dtype=MODEL_NEXT_DTYPE,
            ) / (self.image_sum if self.image_sum else 1)

            dispersion_y = np.sum(
                np.tile(
                    np.arange(0, self.image.shape[1], dtype=MODEL_NEXT_SIGNED_DTYPE)
                    - self.object_center[1],
                    (self.image.shape[0], 1),
                )
                ** 2
                * self.image_weight,
                dtype=MODEL_NEXT_DTYPE,
            ) / (self.image_sum if self.image_sum else 1)

            self._object_dispersion_sq = np.asarray([dispersion_x, dispersion_y])

        return self._object_dispersion_sq

    @property
    def object_pixel_size(self):
        if self._object_pixel_size is None:
            self._object_pixel_size = np.sqrt(self.object_dispersion_sq) * PIXEL_SIZE_COEFFICIENT

        return self._object_pixel_size

    # Function returning boolean of object presence
    def check_object(self, new_image=None):
        if new_image is not None:
            self.image = new_image

        return bool(self.image_sum >= self.threshold_object)

    # Function creating a mask image of raw object
    def get_debug_raw(self):
        r_layer, g_layer = (
            np.where(
                self.image_weight_raw == 0,
                0,
                self.image_weight_raw // MODEL_IMAGE_CAST,
            ).astype(np.uint8)
            for _ in range(2)
        )
        b_layer = np.where(
            self.image_weight_raw == 0,
            255,
            self.image_weight_raw // MODEL_IMAGE_CAST,
        ).astype(np.uint8)

        return np.dstack(tuple(np.asarray(layer) for layer in (r_layer, g_layer, b_layer)))

    # Function creating a mask image of object
    def get_debug(self, *, cross_hair=True):
        r_layer = (self.image_weight // MODEL_IMAGE_CAST).astype(np.uint8)

        g_layer = np.where(
            np.logical_and(self.image_weight == 0, self.image_weight_raw != 0),
            200,
            self.image_weight // MODEL_IMAGE_CAST,
        ).astype(np.uint8)

        b_layer = np.where(
            self.image_weight == 0,
            255,
            self.image_weight // MODEL_IMAGE_CAST,
        ).astype(np.uint8)

        image_grayscale = np.dstack((r_layer, g_layer, b_layer))

        if cross_hair:
            cross_color = (
                np.asarray([0, 255, 0], dtype='uint8')
                if self.check_object()
                else np.asarray([255, 0, 0], dtype='uint8')
            )

            size_x, size_y = self.object_pixel_size

            obj_x, obj_y = self.object_center
            for i in range(-int(size_x), int(size_x) + 1):
                if 0 <= int(obj_x) + i < image_grayscale.shape[0]:
                    image_grayscale[int(obj_x) + i][int(obj_y)] = cross_color
            for i in range(-int(size_y), int(size_y) + 1):
                if 0 <= int(obj_y) + i < image_grayscale.shape[1]:
                    image_grayscale[int(obj_x)][int(obj_y) + i] = cross_color

        return image_grayscale


class RGBModel(InferenceModel):
    def __init__(self, model_path, **kwargs):
        def get_image_weight(image):
            rgb_data = image // RGB_COMPRESSION

            transposed = rgb_data.transpose((2, 0, 1))

            return model[transposed[0], transposed[1], transposed[2]]

        model = np.load(model_path)

        super().__init__(get_image_weight, **kwargs)


class HSVModel(InferenceModel):
    def __init__(self, model_path, **kwargs):
        def get_image_weight(image):
            hsv_data = rgb_to_hsv(image)

            hsv_data[:, :, 0] //= H_COMPRESSION
            hsv_data[:, :, 1] //= S_COMPRESSION
            hsv_data[:, :, 2] //= V_COMPRESSION

            transposed = hsv_data.transpose((2, 0, 1))

            return model[transposed[0], transposed[1], transposed[2]]

        model = np.load(model_path)

        super().__init__(get_image_weight, **kwargs)
