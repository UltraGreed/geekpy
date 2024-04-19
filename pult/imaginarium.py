#!python3
import math
import os.path
import sys

import tkinter

import imageio.v3 as iio
from PIL import ImageTk, Image

from base import network

import setproctitle
setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.


# Path prefix to show image.
PATH_PREFIX = sys.argv[1]
# Objects can be provided in two ways:
#   as "Object.Sub_object" e.g. "Front.left"
#   or as "Object" e.g. "Front"
OBJECTS = [tuple(obj.split('.')) if '.' in obj else obj for obj in sys.argv[2:]]

n_cols = math.ceil(math.sqrt(len(OBJECTS)))
n_rows = math.ceil(len(OBJECTS) / n_cols)

root_tk = tkinter.Tk()
root_tk.title('Imaginarium')

start_image = os.path.dirname(__file__) + '/image_absent.png'

image_widgets = dict()
label_widgets = dict()

for i, obj in enumerate(OBJECTS):
    image_widgets[obj] = ImageTk.PhotoImage(Image.fromarray(iio.imread(start_image)).resize((512, 512)))

    label_widgets[obj] = tkinter.Label(root_tk, image=image_widgets[obj])

    label_widgets[obj].grid(row=i // n_cols, column=i % n_cols, sticky='nsew')


# Update plots in infinite loop.
net = network.Net(timer=0.25)
while net.receive():
    # New image has come.
    if net.id.startswith("ImageLink"):
        no_sub_obj = False  # Break after first provided image shown
        for sub_obj, path in net.msg.path.items():
            # If no sub_obj was selected, show first one
            if net.msg.obj in OBJECTS:
                obj = net.msg.obj
                no_sub_obj = True
            # Show only selected sub_obj
            elif (net.msg.obj, sub_obj) in OBJECTS:
                obj = (net.msg.obj, sub_obj)
            else:
                continue

            link = PATH_PREFIX + path
            label_widget = label_widgets[obj]

            try:
                image_widgets[obj] = ImageTk.PhotoImage(Image.fromarray(iio.imread(link)))
            except TimeoutError:
                print("hz cheto upalo v imaginariume")
                continue

            label_widget.config(image=image_widgets[obj])

            if no_sub_obj:
                break

    if net.id == 'Timer':
        root_tk.update()
        root_tk.update_idletasks()

