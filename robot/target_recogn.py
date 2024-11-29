import sys
import time
import setproctitle

from base import network, message

from object_recognition.model_class import RGBModel, HSVModel, get_model_path
from object_recognition.image_utils import load_image_rgb, save_image_rgb
from object_recognition.object_position import get_yaw_from_pixel
from object_recognition.config import *

#####################
# CONFIG PARAMETERS #
MODEL_PATH_PREFIX = '../object_recognition/'

DEBUG = True
####################


def main(camera_name, model_name, camera_eye):
    if COLOR_SCHEME == 'HSV':
        model = HSVModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    elif COLOR_SCHEME == "RGB":
        model = RGBModel(MODEL_PATH_PREFIX + get_model_path(obj_name=model_name))
    else:
        raise Exception

    net = network.Net()
    while net.receive():
        if net.id == "ImageLinkCameraStereo":
            if net.msg.obj == camera_name:
                time1 = time.time()
                image = load_image_rgb(net.msg.path[camera_eye])

                is_obj_found = model.check_object(image)

                if is_obj_found:
                    if camera_name == 'Front':
                        offset_yaw = float(get_yaw_from_pixel(
                            model.image.shape,
                            model.object_center
                        ))
                    else:
                        raise Exception("Wrong camera name")

                    net.send(message.Target(
                        offset_yaw=offset_yaw,
                        is_detected=True
                    ))

                else:
                    net.send(message.Target(is_detected=False))

                # Saving black and white image with detected object for debugging
                if DEBUG:
                    save_path = net.msg.path[camera_eye].replace('.png', '_gray.png')

                    image_grayscale = model.get_debug()

                    save_image_rgb(save_path, image_grayscale)

                    net.send(message.ImageLinkRecognition(
                        obj=camera_name + 'Target',
                        path=save_path,
                        counter=None
                    ))

                time2 = time.time()
                if time2 - time1 > 0.25:
                    print(f"Image recognition slower than 0.25s: {time2 - time1}")


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

    main(camera_name=sys.argv[1], model_name=sys.argv[2], camera_eye=sys.argv[3])
