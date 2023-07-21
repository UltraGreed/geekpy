import sys

from PIL import Image
import numpy as np
import setproctitle

from base import network, message, mat
from base.message import X, Y, DEPTH

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
def save_bw_image(image, point_coords, save_path):
    image_bw_array = vec_get_bw(image)

    image_bw = Image.fromarray(image_bw_array.astype('uint8'))

    image_bw.putpixel(point_coords, (255, 0, 0))

    image_bw.save(save_path)


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

    net = network.Net()
    while net.receive():
        if net.id == "ImageLink":
            print(0)
            if net.msg.obj == camera_name:
                print(1)
                camera_dist = obj_depth - pos[DEPTH]

                image = Image.open(net.msg.path)
                image_array = np.asarray(image)

                mask = vec_get_mask(image_array)

                y_coords, x_coords = mask.nonzero()

                obj_x, obj_y = round(np.average(x_coords)), round(np.average(y_coords))

                map_coords = get_map_coords(image_array, (obj_x, obj_y, obj_depth), pos, camera_dist)

                net.send(message.DetectedObject(x=map_coords[0], y=map_coords[1]))

                # Saving black and white image with detected object for debugging
                save_path = net.msg.path.replace('.jpg', '_bw.jpg')
                file_path = net.msg.file.replace('.jpg', '_bw.jpg')

                save_bw_image(image_array, (obj_x, obj_y), save_path)

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

