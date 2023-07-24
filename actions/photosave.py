import sys
import time

sys.path.append('./')
from base import message, network
from base.timer import Timer


def photosave_start(camera, path):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOn(camera, path))
		time.sleep(0.01)


def photosave_stop(camera):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOff(camera))
		time.sleep(0.01)


