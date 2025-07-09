import sys
import time
from pathlib import Path

from image_utils import load_image_rgba, save_image_rgba, save_image_rgb

import numpy as np
import cv2


def merge(background_img: np.ndarray,
          object_img: np.ndarray,
          x_offset: int,
          y_offset: int,
          size_scale: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Return merged image from given bg and obj images with given offset of xy and size.

    Object image should be of the same size as background image. Or not. I'm not sure.
    """

    scaled_obj_img = cv2.resize(object_img, (0, 0), fx=size_scale, fy=size_scale)

    new_image = np.zeros((
        int(max(background_img.shape[0], scaled_obj_img.shape[0]) + abs(y_offset)),
        int(max(background_img.shape[1], scaled_obj_img.shape[1]) + abs(x_offset)),
        4
    ))

    # Determining object and bg parts of image depending on x_off and y_off signs
    bg_slices = [None, None]
    obj_slices = [None, None]

    if x_offset >= 0:
        bg_slices[1] = slice(0, background_img.shape[1])
        obj_slices[1] = slice(x_offset, scaled_obj_img.shape[1] + x_offset)
    else:
        bg_slices[1] = slice(-x_offset, background_img.shape[1] - x_offset)
        obj_slices[1] = slice(0, scaled_obj_img.shape[1])

    if y_offset >= 0:
        bg_slices[0] = slice(0, background_img.shape[0])
        obj_slices[0] = slice(y_offset, scaled_obj_img.shape[0] + y_offset)
    else:
        bg_slices[0] = slice(-y_offset, background_img.shape[0] - y_offset)
        obj_slices[0] = slice(0, scaled_obj_img.shape[0])

    new_image[*bg_slices] = background_img

    new_image[*obj_slices] = np.where(
        (scaled_obj_img[..., 3] != 0)[:, :, np.newaxis],
        scaled_obj_img,
        new_image[*obj_slices]
    )

    new_image_labeled = new_image.copy()
    new_image_labeled[obj_slices[0], obj_slices[1], 3] = np.where(
        scaled_obj_img[..., 3] != 0,
        np.zeros_like(new_image[*obj_slices, 3]),
        new_image[*obj_slices, 3]
    )

    new_image = new_image[*bg_slices]
    new_image_labeled = new_image_labeled[*bg_slices]

    return new_image, new_image_labeled


def option_merge(bg_img, obj_img, save_path, x_range, y_range, size_range, n_steps):
    """
    Create a set of images from given bg and obj images within a given ranges of offsets.
    """
    i = 0
    # TODO: fix for n_steps < 2 and zero delta values
    for dx in np.arange(-x_range, x_range + 1, 2 * x_range // (n_steps - 1)):
        for dy in np.arange(-y_range, y_range + 1, 2 * y_range // (n_steps - 1)):
            for dsize in np.arange(-size_range, size_range + 2 * size_range / n_steps, 2 * size_range / (n_steps - 1)):
                time_start = time.time()
                merged_img, merged_img_labeled = merge(bg_img, obj_img, dx, dy, 1 + dsize)

                save_image_rgb(str(save_path / f'{i}.png'), merged_img)
                save_image_rgba(str(save_path / f'{i}_labeled.png'), merged_img_labeled)
                print(f'Image {i} merged in {time.time() - time_start:0.2f}s')
                i += 1


def main(bg_path_str, obj_path_str, save_path_str, x_range, y_range, size_range, n_steps):
    bg_img = load_image_rgba(bg_path_str)
    obj_img = load_image_rgba(obj_path_str)

    save_path = Path(save_path_str)
    save_path.mkdir(parents=True, exist_ok=True)

    option_merge(bg_img, obj_img, save_path, x_range, y_range, size_range, n_steps)


if __name__ == '__main__':
    if len(sys.argv) == 4:
        main(*sys.argv[1:])
    else:
        base_path = Path('images/generated')
        main(
            str(base_path / 'background.png'),
            str(base_path / 'object.png'),
            str(base_path / 'result'),
            x_range=200,
            y_range=100,
            size_range=0,
            n_steps=2
        )
