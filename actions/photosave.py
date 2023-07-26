import sys
import time
from datetime import datetime

sys.path.append('./')
from base import message, network
from base.timer import Timer


def start(camera, path):
	net = network.Net()

	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOn(camera, path))
		time.sleep(0.01)


def stop(camera):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOff(camera))
		time.sleep(0.01)


