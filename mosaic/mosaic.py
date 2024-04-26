import json
import math
import os

import cv2
import numpy as np

from object_recognition.image_utils import load_image_hsv, save_image_hsv

from base.config import BOTTOM_CAMERA_VFOV, BOTTOM_CAMERA_HFOV


# from bbalance import get_bright_balance_hsv
# from image_cross import rects_cross


# from sharr import sharr


class PilotData:
    def __init__(self, file_name, x, y, depth, yaw, time):
        self.file_name = file_name
        self.x = x * 0.6
        self.y = -y * 0.5
        self.depth = depth
        self.yaw = yaw
        self.time = time


class ImageData:
    def __init__(self, array: np.ndarray, x: float, y: float, angle: float):
        self.array = array
        self.x = x
        self.y = y
        self.angle = angle
        self.marked_points = []


working_dir_path = "."
load_photo_dir_path = f'{working_dir_path}/line_with_data'
save_photo_dir_path = working_dir_path
description_path = f'{working_dir_path}/image_datas.json'

PIXEL_PER_METER = 140

IS_MERGE = True

# Сдвиг камеры относительно датчиков
CAM_OFFSET = np.array((0, 0))

BOTTOM_DEPTH = 1

"""
{
    'x': 0.2913306912096712,
    'y': 3.2334247613723055,
    'depth': 0.9366979850456119,
    'yaw': -100.31737723374638,
    'time': '2024-04-23 19:32:07.340180',
    'file_name': '00186.png'
}
"""


def get_scaled_shape(altitude, fov_w, fov_h):
    area_width = 2 * altitude * math.tan(np.deg2rad(fov_w / 2))
    area_height = 2 * altitude * math.tan(np.deg2rad(fov_h / 2))

    pixel_width = round(PIXEL_PER_METER * area_width)
    pixel_height = round(PIXEL_PER_METER * area_height)

    return pixel_width, pixel_height


def get_rotated_shape(angle, width, height):
    rotated_shape = (
        int(abs(math.cos(angle)) * height +
            abs(math.sin(angle)) * width),

        int(abs(math.sin(angle)) * height +
            abs(math.cos(angle)) * width)
    )

    return rotated_shape


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


def rel_to_abs(points: tuple[np.ndarray, np.ndarray]):
    ys, xs = points


def main():
    with open(description_path, mode='r') as file:
        data = json.load(file)

    pilot_datas = list()
    for entry in data:
        pilot_datas.append(PilotData(**entry))

    # Вычисляем необходимые максимальные значения в массиве изображений
    max_x, min_x, max_y, min_y, = None, None, None, None
    max_width, max_height = None, None

    for pilot in pilot_datas:
        if min_x is None or pilot.x < min_x:
            min_x = pilot.x
        if max_x is None or pilot.x > max_x:
            max_x = pilot.x
        if min_y is None or pilot.y < min_y:
            min_y = pilot.y
        if max_y is None or pilot.y > max_y:
            max_y = pilot.y

        rotated_shape = get_rotated_shape(
            pilot.yaw,
            *get_scaled_shape(BOTTOM_DEPTH - pilot.depth, BOTTOM_CAMERA_VFOV, BOTTOM_CAMERA_HFOV)
        )
        if max_width is None or rotated_shape[0] > max_width:
            max_width = rotated_shape[0]
        if max_height is None or rotated_shape[1] > max_height:
            max_height = rotated_shape[1]

    # Разрешение мозаики считается в соответствии с заданным пиксель/метр и небольшим запасом :)
    img_mosaic_res = (
        round(((max_x - min_x) * PIXEL_PER_METER + max_width) * 1.1),
        round(((max_y - min_y) * PIXEL_PER_METER + max_height) * 1.1)
    )

    # Отступы, гарантирующие, что картинка не вылезет за ноль.
    # Равняются количеству пикселей, добавленных к полотну слева сверху
    offset_x = round(max_width / 2)
    offset_y = round(max_height / 2)

    img_mosaic = np.zeros((img_mosaic_res[1], img_mosaic_res[0], 3))
    img_mosaic_counter = np.zeros((img_mosaic_res[1], img_mosaic_res[0]))

    image_datas: list[ImageData] = list()

    first = 0
    last = 100

    for i, pilot in enumerate(pilot_datas):
        img_path = f'{load_photo_dir_path}/right_{pilot.file_name}'
        if i < first:
            continue
        if i > last:
            break

        if i % 16 != 0:
            continue

        if os.path.exists(img_path):
            image_arr = load_image_hsv(img_path)

            # image_arr = get_bright_balance_hsv(image_arr)

            # Размеры изображения в соответствии с масштабом (в пикселях)
            area_res = get_scaled_shape(BOTTOM_DEPTH - pilot.depth, BOTTOM_CAMERA_VFOV, BOTTOM_CAMERA_HFOV)

            image_arr = cv2.resize(image_arr, area_res)

            # Учитываем сдвиг камеры относительно датчиков
            camera_offset = rotate(CAM_OFFSET, -np.deg2rad(pilot.yaw))

            camera_x = pilot.x + camera_offset[0]
            camera_y = pilot.y + camera_offset[1]

            image_datas.append(ImageData(
                image_arr,
                round(PIXEL_PER_METER * (camera_x - min_x)) + offset_x,
                round(PIXEL_PER_METER * (camera_y - min_y)) + offset_y,
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

    # image.y += global_offset[0]
    # image.x += global_offset[1]

    # # Ищем точки пересечения
    # points = rects_cross(
    #     (image.x, image.y), image.array.shape[1::-1], math.radians(image.angle),
    #     (prev_image.x, prev_image.y), prev_image.array.shape[1::-1], math.radians(prev_image.angle),
    # )
    #
    # if not points:
    #     continue
    #
    # # Переводим точки пересечения в относительные координаты
    # points_rel1 = [
    #     rotate((point[0] - prev_image.x, point[1] - prev_image.y),
    #            math.radians(prev_image.angle))
    #     for point in points
    # ]
    # points_rel1 = [
    #     (point[0] + prev_image.array.shape[1] // 2,
    #      point[1] + prev_image.array.shape[0] // 2)
    #     for point in points_rel1
    # ]
    #
    # points_rel2 = [
    #     rotate((point[0] - image.x, point[1] - image.y),
    #            math.radians(image.angle))
    #     for point in points
    # ]
    # points_rel2 = [
    #     (point[0] + image.array.shape[1] // 2,
    #      point[1] + image.array.shape[0] // 2)
    #     for point in points_rel2
    # ]
    #
    # # Достроить до прямоугольников зоны пересечения
    # min_x1 = int(min(points_rel1, key=lambda point: point[0])[0])
    # max_x1 = int(max(points_rel1, key=lambda point: point[0])[0])
    # min_y1 = int(min(points_rel1, key=lambda point: point[1])[1])
    # max_y1 = int(max(points_rel1, key=lambda point: point[1])[1])
    #
    # min_x2 = int(min(points_rel2, key=lambda point: point[0])[0])
    # max_x2 = int(max(points_rel2, key=lambda point: point[0])[0])
    # min_y2 = int(min(points_rel2, key=lambda point: point[1])[1])
    # max_y2 = int(max(points_rel2, key=lambda point: point[1])[1])
    #
    # # Применяем оператор Щарра на изображения
    # sharr1 = sharr(prev_image.array[min_y1:max_y1, min_x1:max_x1])
    # sharr2 = sharr(image.array[min_y2:max_y2, min_x2:max_x2])
    #
    # # Ищем n максимальных точек
    # n_points = 100
    # max_points1 = n_max(sharr1, n_points)
    # prev_image.array[max_points1] = np.asarray((125, 255, 255))
    # max_points2 = n_max(sharr2, n_points)
    # image.array[max_points2] = np.asarray((0, 255, 255))
    #
    # # Переводим точки в абсолютные координаты
    # points_abs1 = (max_points1[0] - prev_image.array.shape[1] // 2,
    #                max_points1[1] - prev_image.array.shape[0] // 2)
    #
    # points_abs1 = rotate((points_abs1[0] + prev_image.x, points_abs1[1] + prev_image.y),
    #                      -math.radians(prev_image.angle))
    #
    # points_abs2 = (max_points2[0] - image.array.shape[1] // 2,
    #                max_points2[1] - image.array.shape[0] // 2)
    #
    # points_abs2 = rotate((points_abs2[0] + image.x, points_abs2[1] + image.y),
    #                      -math.radians(image.angle))
    #
    # # Комбинации всех точек первой и второй картинок
    # xv1, xv2 = np.meshgrid(points_abs1[0], points_abs2[0])
    # yv1, yv2 = np.meshgrid(points_abs1[1], points_abs2[1])
    #
    # delta_coords = (xv1 - xv2).flatten(), (yv1 - yv2).flatten()
    # delta_min_x = int(math.ceil(delta_coords[0].min()))
    # delta_min_y = int(math.ceil(delta_coords[1].min()))
    # delta_coords = (np.asarray(np.round(delta_coords[0]), dtype=np.int64),
    #                 np.asarray(np.round(delta_coords[1]), dtype=np.int64))
    #
    # size = (delta_coords[0].max() - delta_min_x + 2,
    #         delta_coords[1].max() - delta_min_y + 2)

    # # Матрица счётчик наиболее вероятного смещения
    # counter = np.zeros(size, dtype=np.uint32)
    #
    # np.add.at(counter, (delta_coords[0] - delta_min_x, delta_coords[1] - delta_min_y), 1)
    #
    # offset = np.unravel_index(np.argmax(counter), counter.shape)
    # offset = offset[0] + delta_min_x, offset[1] + delta_min_y

    # image.y += offset[0]
    # image.x += offset[1]

    # global_offset[0] += offset[0]
    # global_offset[1] += offset[1]

    # prev_image.array[min_y1:max_y1, min_x1:max_x1] = 179
    # image.array[min_y2:max_y2, min_x2:max_x2] = 179

    # print(offset)

    # Вписываем картинки в мозаику
    for image in image_datas:
        # Оптимальное разрешение картинки после поворота
        rotated_shape = get_rotated_shape(math.radians(image.angle), *image.array.shape[:2])

        image_center = (image.array.shape[1] // 2, image.array.shape[0] // 2)
        new_image_center = (rotated_shape[0] // 2, rotated_shape[1] // 2)

        # Строим матрицу поворота
        rotation_mat = cv2.getRotationMatrix2D(center=image_center, angle=-image.angle, scale=1)

        rotation_mat[:, 2] += np.asarray(new_image_center) - np.asarray(image_center)

        # Применяем аффинное преобразование на картинку
        image.array = cv2.warpAffine(image.array, rotation_mat, rotated_shape, flags=cv2.INTER_NEAREST)

        x_lower = image.x - image.array.shape[1] // 2
        x_upper = x_lower + image.array.shape[1]
        y_lower = image.y - image.array.shape[0] // 2
        y_upper = y_lower + image.array.shape[0]

        if IS_MERGE:
            img_mosaic[y_lower:y_upper, x_lower:x_upper, :] += image.array
        else:
            img_mosaic[y_lower:y_upper, x_lower:x_upper, :] = np.where(
                image.array != 0,
                image.array,
                img_mosaic[y_lower:y_upper, x_lower:x_upper, :]
            )

        img_mosaic_counter[y_lower:y_upper, x_lower:x_upper] += np.sum(image.array, axis=2) != 0

    division_matrix = np.tile(img_mosaic_counter[:, :, np.newaxis], 3)
    division_matrix[division_matrix == 0] = 1

    if IS_MERGE:
        img_mosaic /= division_matrix

    save_image_hsv(f'{save_photo_dir_path}/mosaic.png', img_mosaic)


if __name__ == '__main__':
    main()
