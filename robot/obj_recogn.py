import sys

import numpy as np
import setproctitle

from base import network, message, mat
from base.message import X, Y, DEPTH

from object_recognition.model_class import Model, get_model_inference_path
from object_recognition.image_utils import load_image_rgb, save_image_rgb

#####################
# CONFIG PARAMETERS #
MODEL_PATH_PREFIX = '../object_recognition/'

CAMERA_FOV = 70

DEBUG = True
####################


# Function converting pixel coordinates to map coordinates
def get_rel_from_pixel(image, obj_coords, camera_dist):
    pixel_relative_x = image.shape[X] / 2 - obj_coords[X]
    pixel_relative_y = obj_coords[Y] - image.shape[Y] / 2

    relative_x = pixel_relative_y / image.shape[Y] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist
    relative_y = pixel_relative_x / image.shape[X] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist

    return relative_x, relative_y


def main(camera_name, model_name, obj_name):
    robot_pos = [0 for _ in range(6)]

    model = Model(MODEL_PATH_PREFIX + get_model_inference_path(model_name, obj_name))

    net = network.Net()
    while net.receive():
        if net.id == "ImageLink":
            if net.msg.obj == camera_name:
                image = load_image_rgb(net.msg.path)

                is_obj_found = model.check_object(image)

                if is_obj_found:
                    if camera_name == 'Bottom':
                        obj_depth = message.FilteredObjects().objs[obj_name][DEPTH]

                        camera_dist = obj_depth - robot_pos[DEPTH]

                        relative_x, relative_y = get_rel_from_pixel(image, model.object_center, camera_dist)

                        map_x, map_y, map_depth = mat.robot2map(robot_pos, (relative_x, relative_y, obj_depth - robot_pos[DEPTH]))
                    elif camera_name == 'Front':
                        camera_dist = 1

                        relative_x, relative_depth = get_rel_from_pixel(image, model.object_center, camera_dist)

                        relative_y = camera_dist * np.cos(np.deg2rad(CAMERA_FOV / 2))

                        map_x, map_y, map_depth = mat.robot2map(robot_pos, (relative_x, relative_y, relative_depth))
                    else:
                        raise Exception

                    net.send(message.DetectedObject(x=float(map_x), y=float(map_y), depth=float(map_depth), obj=obj_name))

                # Saving black and white image with detected object for debugging
                if DEBUG:
                    save_path = net.msg.path.replace('.png', '_gray.png')
                    file_path = net.msg.file.replace('.png', '_gray.png')

                    image_grayscale = model.get_grayscale()

                    obj_x, obj_y = model.object_center

                    image_grayscale[int(obj_x)][int(obj_y)] = np.asarray([255, 0, 0], dtype='uint8')

                    cross_color = np.asarray([0, 255, 0], dtype='uint8') \
                        if is_obj_found else \
                        np.asarray([255, 0, 0], dtype='uint8')

                    for i in range(-3, 3 + 1):
                        image_grayscale[int(obj_x) + i][int(obj_y)] = cross_color
                        image_grayscale[int(obj_x)][int(obj_y) + i] = cross_color

                    save_image_rgb(save_path, image_grayscale)

                    net.send(message.ImageLink(
                        path=save_path,
                        obj=camera_name + obj_name,
                        file=file_path,
                        counter=None
                    ))

        if net.id == "Coord":
            robot_pos = net.msg.pos


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(camera_name=sys.argv[1], model_name=sys.argv[2], obj_name=sys.argv[3])
