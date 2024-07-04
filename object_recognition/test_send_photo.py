from os import walk, path
from time import sleep
import sys

from base import network
from base import message

FOLDER_PATH = path.abspath(sys.argv[1])
OBJECT = tuple(sys.argv[2].split("."))


files = []
for (dirpath, dirnames, filenames) in walk(FOLDER_PATH):
    files.extend(filenames)
    break

net = network.Net()

for it in files:
    msg = message.ImageLinkCameraStereo(obj=OBJECT[0], path_right=f"{FOLDER_PATH}/{it}")
    net.send(msg)
    sleep(0.1)
