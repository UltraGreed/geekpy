import sys
import time
import setproctitle

from pathlib import Path

from base import network, message
from base.message import X, Y, DEPTH, DIAMETER

from object_recognition.model_class import RGBModel, HSVModel, get_model_path
from object_recognition.image_utils import load_image_rgb, save_image_rgb, crop, meters_to_pixels
from object_recognition.object_position import get_obj_pos_front, get_obj_pos_bottom, CAMERA_FOV
from object_recognition.config import *
from robot.line_recogn import meters_to_pixels

#####################
# CONFIG PARAMETERS #
MODEL_PATH_PREFIX = '../object_recognition/'

DEBUG = True
####################


def main(camera_path: str, model_name: str, obj_name: str, visible_range: float):
    """
    :param camera_path: camera.eye to listen to
    :param model_name: np model to use in inference
    :param obj_name: object to publish
    :param visible_range: side of visible area of the floor
    :return:
    """
    camera_name, camera_eye = camera_path.split('.')
    robot_pos = [0 for _ in range(6)]

    if COLOR_SCHEME == 'HSV':
        model = HSVModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    elif COLOR_SCHEME == "RGB":
        model = RGBModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    else:
        raise Exception

    object_depth = network.wait_message(message.FilteredObjects.id).objs[obj_name][2]

    net = network.Net()
    while net.receive():
        if net.id == "ImageLinkCameraStereo":
            if net.msg.obj == camera_name:
                time1 = time.time()
                image = load_image_rgb(net.msg.path[camera_eye])

                smaller_side = min(image.shape[:2])
                image = crop(image, (smaller_side, smaller_side))

                new_size = int(meters_to_pixels(
                    visible_range,
                    object_depth - robot_pos[DEPTH],
                    CAMERA_FOV,
                    image.shape[1]
                ))
                shape_ratio = image.shape[0] / image.shape[1]
                image = crop(image, (int(new_size * shape_ratio), new_size))

                is_obj_found = model.check_object(image)

                if is_obj_found:
                    if camera_name == 'Bottom':
                        obj_depth = message.FilteredObjects().objs[obj_name][DEPTH]
                        obj_coords = get_obj_pos_bottom(
                            robot_pos,
                            obj_depth,
                            model.image.shape,
                            model.object_center
                        )
                    elif camera_name == 'Front':
                        obj_size = message.FilteredObjects().objs[obj_name][DIAMETER]
                        obj_coords = get_obj_pos_front(
                            robot_pos,
                            obj_size,
                            model.object_pixel_size,
                            model.image.shape,
                            model.object_center
                        )
                    else:
                        raise Exception

                    net.send(message.DetectedObject(
                        x=float(obj_coords[X]),
                        y=float(obj_coords[Y]),
                        depth=float(obj_coords[DEPTH]),
                        obj=obj_name
                    ))

                # Saving black and white image with detected object for debugging
                if DEBUG:
                    original_filename = Path(net.msg.path[camera_eye]).with_suffix('')
                    original_ext = Path(net.msg.path[camera_eye]).suffix

                    save_path = f'{original_filename}_{obj_name}_gray{original_ext}'

                    image_grayscale = model.get_debug()

                    save_image_rgb(save_path, image_grayscale)

                    net.send(message.ImageLinkRecognition(
                        obj=camera_name + obj_name,
                        path=save_path,
                        counter=None
                    ))

                time2 = time.time()
                if time2 - time1 > 0.25:
                    print(f"Image recognition slow: {time2 - time1}")

        if net.id == "Coord":
            robot_pos = net.msg.pos


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(
        camera_path=sys.argv[1],
        model_name=sys.argv[2],
        obj_name=sys.argv[3],
        visible_range=float(sys.argv[4])
    )
