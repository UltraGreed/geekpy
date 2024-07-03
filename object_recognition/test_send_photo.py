from os import walk
from time import sleep
import sys

from base import network
from base import message

FOLDER_PATH = sys.argv[1]
OBJECT = tuple(sys.argv[2].split("."))


files = []
for (dirpath, dirnames, filenames) in walk(FOLDER_PATH):
    files.extend(filenames)
    break

net = network.Net()
msg = message.ImageLink(obj=OBJECT[0], path={OBJECT[1]: ""})

for it in files:
    msg.path[OBJECT[1]] = FOLDER_PATH + it
    net.send(msg)
    sleep(0.5)
