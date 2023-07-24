import sys

from PIL import Image
import numpy as np
import setproctitle

from base import network, message, mat
from base.message import X, Y, DEPTH

from object_recognition.model_class import Model
from object_recognition.image_utils import load_image_rgba, save_image_rgba

#####################
# CONFIG PARAMETERS #
THRESHOLD_COLOR = 10 ** 2
TARGET_COLOR = np.array([49.8, 69.4, 16.4])

THRESHOLD_IMAGE_PART = 0.1

CAMERA_FOV = 70


####################

# Function converting pixel coordinates to map coordinates
def get_map_coords(image, obj_coords, robot_coords, camera_dist):
    pixel_relative_x = obj_coords[X] - image.shape[X] / 2
    pixel_relative_y = image.shape[Y] / 2 - obj_coords[Y]

    relative_x = pixel_relative_x / image.shape[0] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist
    relative_y = pixel_relative_y / image.shape[1] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist

    return mat.robot2map(robot_coords, (relative_x, relative_y, obj_coords[DEPTH]))


def main(camera_name, obj_name):
    pos = [0 for _ in range(6)]
    obj_depth = message.FilteredObjects().objs[obj_name][DEPTH]

    model = Model()

    net = network.Net()
    while net.receive():
        if net.id == "ImageLink":
            if net.msg.obj == camera_name:
                camera_dist = obj_depth - pos[DEPTH]

                image = Image.open(net.msg.path)
                image_array = np.asarray(image)

                mask = model.get_mask(image_array)

                y_coords, x_coords = mask.nonzero()

                if len(y_coords) >= THRESHOLD_IMAGE_PART * len(image_array):
                    obj_x, obj_y = round(np.average(x_coords)), round(np.average(y_coords))

                    map_coords = get_map_coords(image_array, (obj_x, obj_y, obj_depth), pos, camera_dist)

                    net.send(message.DetectedObject(x=map_coords[0], y=map_coords[1], obj=obj_name))

                    # Saving black and white image with detected object for debugging
                    save_path = net.msg.path.replace('.jpg', '_bw.jpg')
                    file_path = net.msg.file.replace('.jpg', '_bw.jpg')

                    image_bw_array = model.get_grayscale(image_array)

                    image_bw_array[obj_x][obj_y] = np.asarray([255, 0, 0, 255], dtype='uint8')

                    save_image_rgba(save_path, image_bw_array)

                    net.send(message.ImageLink(
                        path=save_path,
                        obj=net.msg.obj,
                        file=file_path
                    ))

        if net.id == "Coord":
            pos = net.msg.pos


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(camera_name=sys.argv[1], obj_name=sys.argv[2])
