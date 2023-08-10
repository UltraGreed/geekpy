#!python3
import math
import setproctitle
import sys
import tkinter

import imageio.v3 as iio
from PIL import ImageTk, Image

from base import network

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
# Path prefix to show image.
PATH_PREFIX = "http://192.168.88.101"
OBJECTS = sys.argv[1:]

n_cols = math.ceil(math.sqrt(len(OBJECTS)))
n_rows = math.ceil(len(OBJECTS) / n_cols)

# Subscribe to messages.

root = tkinter.Tk()
root.title('Imaginarium')

start_image = 'image_absent.png'

image_widgets = dict()
label_widgets = dict()

is_resizing = False

for i, obj in enumerate(OBJECTS):
    image_widgets[obj] = ImageTk.PhotoImage(Image.fromarray(iio.imread(start_image)).resize((512, 512)))

    label_widgets[obj] = tkinter.Label(root, image=image_widgets[obj])

    label_widgets[obj].grid(row=i // n_cols, column=i % n_cols, sticky='nsew')


# Update plots in infinite loop.
net = network.Net(timer=0.25)
while net.receive():
    # New message has come.
    if net.id == "ImageLink":
        if net.msg.obj not in OBJECTS:
            continue

        link = PATH_PREFIX + net.msg.path
        label_widget = label_widgets[net.msg.obj]

        image_widgets[net.msg.obj] = ImageTk.PhotoImage(Image.fromarray(iio.imread(link)).resize((512, 512)))

        label_widget.config(image=image_widgets[net.msg.obj])

    if net.id == 'Timer':
        root.update()
        root.update_idletasks()

