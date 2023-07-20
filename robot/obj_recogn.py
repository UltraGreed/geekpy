import sys

from PIL import Image
import numpy as np
import setproctitle

from base import network, message, mat
from base.message import DEPTH

#####################
# CONFIG PARAMETERS #
THRESHOLD = 200 ** 2
TARGET_COLOR = np.array([255, 255, 0])
CAMERA_FOV = 70
####################


# Function creating a bit mask of the image
def get_mask(pixel):
    error = np.sum(np.square(pixel - TARGET_COLOR))

    return True if error < THRESHOLD else False


vec_get_mask = np.vectorize(get_mask, signature='(3)->()')


# Function creating a black and white array image of object
def get_bw(pixel):
    error = np.sum(np.square(pixel - TARGET_COLOR))

    return np.array([255, 255, 255]) if error < THRESHOLD else np.array([0, 0, 0])


vec_get_bw = np.vectorize(get_bw, signature='(3)->(3)')


# Function saving black and white image with detected object for debugging
def save_bw_image(image, point_coords):
    image_bw_array = vec_get_bw(image)

    image_bw = Image.fromarray(image_bw_array.astype('uint8'))

    image_bw.putpixel(point_coords, (255, 0, 0))


# Function converting pixel coordinates to map coordinates
def get_map_coords(image, obj_coords, robot_coords, camera_dist):
    pixel_dist_x = image.shape[0] / 2 - obj_coords[0]
    pixel_dist_y = image.shape[1] / 2 - obj_coords[1]

    dist_x = pixel_dist_x / image.shape[0] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist
    dist_y = pixel_dist_y / image.shape[1] * 2 * np.tan(np.deg2rad(CAMERA_FOV / 2)) * camera_dist

    return mat.robot2map(robot_coords, (dist_x, dist_y))


def main(obj_name):
    pos_depth = 0
    obj_depth = message.FilteredObjects().objs[obj_name][DEPTH]

    net = network.Net()
    while net.receive():
        if net.id == "ImageLink":
            if net.msg.obj == obj_name:
                camera_dist = obj_depth - pos_depth

                image = Image.open(net.msg.path)
                image_array = np.asarray(image)

                mask = vec_get_mask(image_array)

                y_coords, x_coords = mask.nonzero()

                obj_x, obj_y = round(np.average(x_coords)), round(np.average(y_coords))

                map_coords = get_map_coords(image_array, (obj_x, obj_y), net.message.pos, camera_dist)

                net.send(message.DetectedObject(x=map_coords[0], y=map_coords[1]))

                # Saving black and white image with detected object for debugging
                save_bw_image(image_array, (obj_x, obj_y))

                net.send(message.ImageLink(
                    path=net.msg.path.replace('.jpg', '_bw.jpg'),
                    obj=net.msg.obj,
                    file=net.msg.file.replace('.jpg', '_bw.jpg')
                ))

        if net.id == "Coord":
            pos_depth = net.message.depth


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(sys.argv[1])

