import sys
import time

import numpy as np
import setproctitle

from base import network, message, mat
from base.message import X, Y, DEPTH, DIAMETER

from object_recognition.model_class import StatisticModel, get_model_inference_path
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


def main(camera_name, model_type, model_name, obj_name):
    robot_pos = [0 for _ in range(6)]

    model = StatisticModel(MODEL_PATH_PREFIX + get_model_inference_path(model_type, model_name))

    net = network.Net()
    while net.receive():
        if net.id == "ImageLink":
            if net.msg.obj == camera_name:
                time1 = time.time()
                image = load_image_rgb(net.msg.path)

                is_obj_found = model.check_object(image)

                if is_obj_found:
                    if camera_name == 'Bottom':
                        obj_depth = message.FilteredObjects().objs[obj_name][DEPTH]

                        camera_dist = obj_depth - robot_pos[DEPTH]

                        relative_x, relative_y = get_rel_from_pixel(image, model.object_center, camera_dist)

                        map_x, map_y, map_depth = mat.robot2map(
                            robot_pos,
                            (relative_x, relative_y, obj_depth - robot_pos[DEPTH])
                        )
                    elif camera_name == 'Front':
                        obj_pixel = model.object_pixel_size
                        obj_size = message.FilteredObjects().objs[obj_name][DIAMETER]

                        camera_dist_x = image.shape[X] / obj_pixel[X] / np.tan(np.deg2rad(CAMERA_FOV / 2)) * obj_size / 2
                        camera_dist_y = image.shape[Y] / obj_pixel[Y] / np.tan(np.deg2rad(CAMERA_FOV / 2)) * obj_size / 2

                        camera_dist = (camera_dist_x + camera_dist_y) / 2

                        relative_x, relative_depth = get_rel_from_pixel(image, model.object_center, camera_dist)
                        relative_depth *= -1

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

                    save_image_rgb(save_path, image_grayscale)

                    net.send(message.ImageLink(
                        path=save_path,
                        obj=camera_name + obj_name,
                        file=file_path,
                        counter=None
                    ))

                time2 = time.time()
                if time2 - time1 > 0.25:
                    print(f"Image all: {time2 - time1}")

        if net.id == "Coord":
            robot_pos = net.msg.pos


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(camera_name=sys.argv[1], model_type=sys.argv[2], model_name=sys.argv[3], obj_name=sys.argv[4])
