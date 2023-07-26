import sys
import time

import numpy as np
import setproctitle

from base import network, message, mat
from base.message import X, Y, DEPTH

from object_recognition.model_class import Model
from object_recognition.image_utils import load_image_rgb, save_image_rgb

#####################
# CONFIG PARAMETERS #
CAMERA_FOV = 70

DEBUG = True
####################


# Function converting pixel coordinates to map coordinates
def get_map_coords(image, obj_coords, robot_coords, camera_dist):
    pixel_relative_x = obj_coords[X] - image.shape[X] / 2
    pixel_relative_y = image.shape[Y] / 2 - obj_coords[Y]

    relative_x = pixel_relative_y / image.shape[1] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist
    relative_y = pixel_relative_x / image.shape[0] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist

    return mat.robot2map(robot_coords, (relative_x, relative_y, obj_coords[DEPTH]))


def main(camera_name, obj_name, model_path):
    pos = [0 for _ in range(6)]
    obj_depth = message.FilteredObjects().objs[obj_name][DEPTH]

    model = Model(model_path)

    net = network.Net()
    while net.receive():
        if net.id == "ImageLink":
            if net.msg.obj == camera_name:
                time1 = time.time()
                camera_dist = obj_depth - pos[DEPTH]

                image = load_image_rgb(net.msg.path)

                is_obj_found = model.check_object(image)

                obj_x, obj_y = model.object_center

                if is_obj_found:
                    map_coords = get_map_coords(image, (obj_x, obj_y, obj_depth), pos, camera_dist)

                    net.send(message.DetectedObject(x=float(map_coords[0]), y=float(map_coords[1]), obj=obj_name))

                # Saving black and white image with detected object for debugging
                if DEBUG:
                    save_path = net.msg.path.replace('.jpg', '_gray.png')
                    file_path = net.msg.file.replace('.jpg', '_gray.png')

                    image_grayscale = model.get_grayscale()

                    image_grayscale[int(obj_x + 0.5)][int(obj_y + 0.5)] = np.asarray([255, 0, 0, 255], dtype='uint8')

                    save_image_rgb(save_path, image_grayscale)

                    net.send(message.ImageLink(
                        path=save_path,
                        obj=net.msg.obj,
                        file=file_path
                    ))
                print(time.time() - time1)

        if net.id == "Coord":
            pos = net.msg.pos


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(camera_name=sys.argv[1], obj_name=sys.argv[2], model_path=sys.argv[3])
