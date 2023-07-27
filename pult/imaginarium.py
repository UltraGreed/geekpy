#!python3 
import io, sys, setproctitle, matplotlib
import numpy as np
import matplotlib.pyplot as plt
import imageio.v3 as io
from base import network

# Path prefix to show image.
#PATH_PERFIX = "https://upload.wikimedia.org/wikipedia/commons/d/d3/"
PATH_PREFIX = "http://192.168.88.101"
OBJ = sys.argv[1]

# Create axes and image plot.
axs = plt.subplot(111)
img = axs.imshow(io.imread("image_absent.png"))
plt.ion()

# Subscribe to messages.
net = network.Net()

# Update plots in infinit loop.
while net.receive():

    # img.set_data(io.imread("Newtons_cradle_animation_book_2.gif"))
    # img.set_data(io.imread("https://placebear.com/g/200/200"))
    # img.set_data(io.imread("image_test.png"))
    # plt.pause(0.001)

    # New message has come.
    if net.id == "ImageLink":
        msg = net.msg
        # print(msg)
        if msg.obj != OBJ:
            continue
        link = PATH_PREFIX + msg.path
        img.set_data(io.imread(link))
        plt.pause(0.001)

plt.ioff()  # Due to infinite loop,
plt.show()  # this gets never called.