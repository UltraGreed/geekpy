import math

from base import mat
from base.message import X, Y, DEPTH

BOTTOM_CAMERA_VFOV = 51.8
BOTTOM_CAMERA_HFOV = 72.4

CAMERA_FOV = 70


# Function converting pixel coordinates to map coordinates
def get_rel_from_pixel(image_shape, obj_coords, camera_dist):
    pixel_relative_x = obj_coords[1] - image_shape[1] // 2
    pixel_relative_y = image_shape[0] // 2 - obj_coords[0]

    # TODO: Split camera FOVs
    relative_x = pixel_relative_x / image_shape[1] * 2 * math.tan(math.radians(BOTTOM_CAMERA_VFOV) / 2) * camera_dist
    relative_y = pixel_relative_y / image_shape[0] * 2 * math.tan(math.radians(BOTTOM_CAMERA_HFOV) / 2) * camera_dist

    return relative_x, relative_y


def get_obj_pos_bottom(robot_pos, obj_depth, image_shape, obj_center):
    camera_dist = obj_depth - robot_pos[DEPTH]

    relative_x, relative_y = get_rel_from_pixel(image_shape, obj_center, camera_dist)

    map_x, map_y, map_depth = mat.robot2map(
        robot_pos,
        (relative_x, relative_y, obj_depth - robot_pos[DEPTH])
    )

    return map_x, map_y, map_depth


def get_obj_pos_front(robot_pos, obj_real, obj_pixel, image_shape, obj_center):
    raise NotImplementedError
    # TODO: Split camera FOVs
    camera_dist_x = image_shape[X] / obj_pixel[X] / math.tan(CAMERA_FOV / 2 / math.pi * 180) * obj_real / 2
    camera_dist_y = image_shape[Y] / obj_pixel[Y] / math.tan(CAMERA_FOV / 2 / math.pi * 180) * obj_real / 2

    camera_dist = (camera_dist_x + camera_dist_y) / 2

    relative_x, relative_depth = get_rel_from_pixel(image_shape, obj_center, camera_dist)
    relative_depth *= -1

    # TODO: Split camera FOVs
    relative_y = camera_dist * math.cos(CAMERA_FOV / 2 / math.pi * 180)

    map_x, map_y, map_depth = mat.robot2map(robot_pos, (relative_x, relative_y, relative_depth))

    return map_x, map_y, map_depth


# Function converting pixel coordinates to map coordinates
def get_yaw_from_pixel(image_shape, obj_coords):
    raise NotImplementedError
    pixel_relative_y = obj_coords[Y] - image_shape[Y] / 2

    offset_yaw = pixel_relative_y / image_shape[Y] * CAMERA_FOV

    return offset_yaw
