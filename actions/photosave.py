import sys
import time
from datetime import datetime

sys.path.append('./')
from base import message, network
from base.timer import Timer


def start(camera, path):
	net = network.Net()

	timer = Timer(0.05)
	while not timer.is_unlock:
		net.send(message.PhotoOn(camera, path))
		time.sleep(0.001)


def stop(camera):
	net = network.Net()

	timer = Timer(0.05)
	while not timer.is_unlock:
		net.send(message.PhotoOff(camera))
		time.sleep(0.001)
