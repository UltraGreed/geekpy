import json
import math
import os

import cv2
import numpy as np

from PIL import Image

from object_recognition.image_utils import load_image_hsv, save_image_hsv, save_image_rgba

from base.config import BOTTOM_CAMERA_VFOV, BOTTOM_CAMERA_HFOV

# from image_cross import rects_cross

# from sharr import sharr

working_dir_path = 'data'
load_photo_dir_path = f'{working_dir_path}'
save_photo_dir_path = 'output'
description_path = f'{load_photo_dir_path}/coord_data.txt'

PIXEL_PER_METER = 280

IS_MERGE = False

BOTTOM_DEPTH = 1.2

# Сдвиг камеры относительно датчиков
CAM_OFFSET = np.array((0, 0))


class PilotData:
    def __init__(self, file_name, x, y, depth, yaw, time):
        self.file_name = file_name
        self.x = x
        self.y = -y
        self.depth = depth
        self.yaw = yaw
        self.time = time


class ImageData:
    def __init__(self, array: np.ndarray, x: float, y: float, angle: float):
        self.array = array
        self.x = x
        self.y = y
        self.marked_points = []
        self._angle = angle
        self._rotated_shape = None

    @property
    def rotated_shape(self):
        if self._rotated_shape is None:
            self._rotated_shape = (
                int(abs(math.sin(self.angle)) * self.array.shape[0] +
                    abs(math.cos(self.angle)) * self.array.shape[1]),
                int(abs(math.cos(self.angle)) * self.array.shape[0] +
                    abs(math.sin(self.angle)) * self.array.shape[1]),
            )
        return self._rotated_shape

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._rotated_shape = None
        self._angle = value


def get_scaled_shape(altitude, fov_w, fov_h):
    area_width = 2 * altitude * math.tan(np.deg2rad(fov_w / 2))
    area_height = 2 * altitude * math.tan(np.deg2rad(fov_h / 2))

    pixel_width = round(PIXEL_PER_METER * area_width)
    pixel_height = round(PIXEL_PER_METER * area_height)

    return pixel_width, pixel_height


def rotate(point, angle):
    """
    Rotate a point counterclockwise by a given angle around an axis origin.

    The angle should be given in radians.
    """
    px, py = point

    qx = math.cos(angle) * px - math.sin(angle) * py
    qy = math.sin(angle) * px + math.cos(angle) * py
    return qx, qy


def n_max(array: np.ndarray, n: int):
    """Returns the n largest indices from a numpy array."""
    flat = array.flatten()
    indices = np.argpartition(flat, -n)[-n:]
    return np.unravel_index(indices, array.shape)


def main():
    with open(description_path) as file:
        datas = json.load(file)

    pilot_datas = [PilotData(**data) for data in datas]

    image_datas: list[ImageData] = list()
    for i, pilot in enumerate(pilot_datas):
        img_path = f'{load_photo_dir_path}/right_{pilot.file_name}'

        if os.path.exists(img_path):
            image_arr = load_image_hsv(img_path)

            # Размеры изображения в соответствии с масштабом (в пикселях)
            area_res = get_scaled_shape(BOTTOM_DEPTH - pilot.depth, BOTTOM_CAMERA_VFOV, BOTTOM_CAMERA_HFOV)

            image_arr = cv2.resize(image_arr, area_res)

            # Учитываем сдвиг камеры относительно датчиков
            camera_offset = rotate(CAM_OFFSET, -np.deg2rad(pilot.yaw))

            camera_x = pilot.x + camera_offset[0]
            camera_y = pilot.y + camera_offset[1]

            image_datas.append(ImageData(
                image_arr,
                int(PIXEL_PER_METER * camera_x),
                int(PIXEL_PER_METER * camera_y),
                pilot.yaw,
            ))

            print(f'File {img_path} processed: {i + 1}/{len(pilot_datas)}')
        else:
            print(f'File {img_path} not found!')
            continue

    # # Выравниваем картинки по предыдущим
    # global_offset = [0, 0]
    # for i, image in enumerate(image_datas[1:], 1):
    #     prev_image = image_datas[i - 1]
    #
    #     image.y += global_offset[0]
    #     image.x += global_offset[1]
    #
    #     # Ищем точки пересечения
    #     points = rects_cross(
    #         (image.x, image.y), image.array.shape[1::-1], math.radians(image.angle),
    #         (prev_image.x, prev_image.y), prev_image.array.shape[1::-1], math.radians(prev_image.angle),
    #     )
    #
    #     if not points:
    #         continue
    #
    #     # Переводим точки пересечения в относительные координаты
    #     points_rel1 = [
    #         rotate((point[0] - prev_image.x, point[1] - prev_image.y),
    #                math.radians(prev_image.angle))
    #         for point in points
    #     ]
    #     points_rel1 = [
    #         (point[0] + prev_image.array.shape[1] // 2,
    #          point[1] + prev_image.array.shape[0] // 2)
    #         for point in points_rel1
    #     ]
    #
    #     points_rel2 = [
    #         rotate((point[0] - image.x, point[1] - image.y),
    #                math.radians(image.angle))
    #         for point in points
    #     ]
    #     points_rel2 = [
    #         (point[0] + image.array.shape[1] // 2,
    #          point[1] + image.array.shape[0] // 2)
    #         for point in points_rel2
    #     ]
    #
    #     # Достроить до прямоугольников зоны пересечения
    #     min_x1 = int(min(points_rel1, key=lambda point: point[0])[0])
    #     max_x1 = int(max(points_rel1, key=lambda point: point[0])[0])
    #     min_y1 = int(min(points_rel1, key=lambda point: point[1])[1])
    #     max_y1 = int(max(points_rel1, key=lambda point: point[1])[1])
    #
    #     min_x2 = int(min(points_rel2, key=lambda point: point[0])[0])
    #     max_x2 = int(max(points_rel2, key=lambda point: point[0])[0])
    #     min_y2 = int(min(points_rel2, key=lambda point: point[1])[1])
    #     max_y2 = int(max(points_rel2, key=lambda point: point[1])[1])
    #
    #     # Применяем оператор Щарра на изображения
    #     sharr1 = sharr(prev_image.array[min_y1:max_y1, min_x1:max_x1])
    #     sharr2 = sharr(image.array[min_y2:max_y2, min_x2:max_x2])
    #
    #     # Ищем n максимальных точек
    #     n_points = 100
    #     max_points1 = n_max(sharr1, n_points)
    #     prev_image.array[max_points1] = np.asarray((125, 255, 255))
    #     max_points2 = n_max(sharr2, n_points)
    #     image.array[max_points2] = np.asarray((0, 255, 255))
    #
    #     # Переводим точки в абсолютные координаты
    #     points_abs1 = (max_points1[0] - prev_image.array.shape[1] // 2,
    #                    max_points1[1] - prev_image.array.shape[0] // 2)
    #
    #     points_abs1 = rotate((points_abs1[0] + prev_image.x, points_abs1[1] + prev_image.y),
    #                          -math.radians(prev_image.angle))
    #
    #     points_abs2 = (max_points2[0] - image.array.shape[1] // 2,
    #                    max_points2[1] - image.array.shape[0] // 2)
    #
    #     points_abs2 = rotate((points_abs2[0] + image.x, points_abs2[1] + image.y),
    #                          -math.radians(image.angle))
    #
    #     # Комбинации всех точек первой и второй картинок
    #     xv1, xv2 = np.meshgrid(points_abs1[0], points_abs2[0])
    #     yv1, yv2 = np.meshgrid(points_abs1[1], points_abs2[1])
    #
    #     delta_coords = (xv1 - xv2).flatten(), (yv1 - yv2).flatten()
    #     delta_min_x = int(math.ceil(delta_coords[0].min()))
    #     delta_min_y = int(math.ceil(delta_coords[1].min()))
    #     delta_coords = (np.asarray(np.round(delta_coords[0]), dtype=np.int64),
    #                     np.asarray(np.round(delta_coords[1]), dtype=np.int64))
    #
    #     size = (delta_coords[0].max() - delta_min_x + 2,
    #             delta_coords[1].max() - delta_min_y + 2)
    #
    #     # Матрица счётчик наиболее вероятного смещения
    #     counter = np.zeros(size, dtype=np.uint32)
    #
    #     np.add.at(counter, (delta_coords[0] - delta_min_x, delta_coords[1] - delta_min_y), 1)
    #
    #     offset = np.unravel_index(np.argmax(counter), counter.shape)
    #     offset = offset[0] + delta_min_x, offset[1] + delta_min_y
    #
    #     # image.y += offset[0]
    #     # image.x += offset[1]
    #
    #     global_offset[0] += offset[0]
    #     global_offset[1] += offset[1]
    #
    #     # prev_image.array[min_y1:max_y1, min_x1:max_x1] = 179
    #     # image.array[min_y2:max_y2, min_x2:max_x2] = 179
    #
    #     print(offset)

    # Поворачиваем картинки
    for image in image_datas:
        # Оптимальное разрешение картинки после поворота
        image_center = (image.array.shape[1] // 2, image.array.shape[0] // 2)
        new_image_center = (image.rotated_shape[1] // 2, image.rotated_shape[0] // 2)

        # Строим матрицу поворота
        rotation_mat = cv2.getRotationMatrix2D(center=image_center, angle=-image.angle, scale=1)

        rotation_mat[:, 2] += np.asarray(new_image_center) - np.asarray(image_center)

        # Применяем аффинное преобразование на картинку
        image.array = cv2.warpAffine(image.array, rotation_mat, image.rotated_shape[::-1], flags=cv2.INTER_NEAREST)

    # Вычисляем необходимые граничные значения в массиве изображений
    max_x, min_x, max_y, min_y, = None, None, None, None
    for image in image_datas:
        lower_y = image.y - image.array.shape[0] // 2
        upper_y = lower_y + image.array.shape[0]
        if min_y is None or lower_y < min_y:
            min_y = lower_y
        if max_y is None or upper_y > max_y:
            max_y = upper_y

        lower_x = image.x - image.array.shape[1] // 2
        upper_x = image.x + image.array.shape[1]
        if min_x is None or lower_x < min_x:
            min_x = lower_x
        if max_x is None or upper_x > max_x:
            max_x = upper_x

    img_mosaic_res = (
        max_y - min_y + 1,
        max_x - min_x + 1
    )

    img_mosaic = np.zeros((*img_mosaic_res, 3))
    img_mosaic_counter = np.zeros(img_mosaic_res)

    # Вписываем картинки в мозаику
    for i, image in enumerate(image_datas):
        x_lower = image.x - image.array.shape[1] // 2 - min_x
        x_upper = x_lower + image.array.shape[1]
        y_lower = image.y - image.array.shape[0] // 2 - min_y
        y_upper = y_lower + image.array.shape[0]

        if IS_MERGE:
            img_mosaic[y_lower:y_upper, x_lower:x_upper] += image.array
        else:
            img_mosaic[y_lower:y_upper, x_lower:x_upper] = np.where(
                image.array != 0,
                image.array,
                img_mosaic[y_lower:y_upper, x_lower:x_upper]
            )

        image.array = cv2.cvtColor(cv2.cvtColor(image.array.astype('uint8'), cv2.COLOR_HSV2RGB), cv2.COLOR_RGB2RGBA)
        # Fill alpha layer
        image.array[:, :, 3][np.all(image.array[:, :, 0:3] == (0, 0, 0), 2)] = 0

        save_image_rgba(f'{save_photo_dir_path}/{str(i).rjust(4, "0")}.png', image.array)

        img_mosaic_counter[y_lower:y_upper, x_lower:x_upper] += np.sum(image.array, axis=2) != 0
        print(f"Image {i} imprinted into mosaic")

    Image.fromarray(np.zeros((*img_mosaic_res, 4), dtype='uint8')).save(
        f'{save_photo_dir_path}/mosaic.tiff',
        save_all=True,
        append_images=[Image.fromarray(image.array) for image in image_datas],
        compression='tiff_lzw'
    )

    division_matrix = np.tile(img_mosaic_counter[:, :, np.newaxis], 3)
    division_matrix[division_matrix == 0] = 1

    if IS_MERGE:
        img_mosaic /= division_matrix

    save_image_hsv(f'{save_photo_dir_path}/mosaic.png', img_mosaic)


if __name__ == '__main__':
    main()
