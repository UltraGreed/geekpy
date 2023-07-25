import sys
import time
from datetime import datetime

sys.path.append('./')
from base import message, network
from base.timer import Timer


def start(camera, path):
	net = network.Net()

	real_path = f'{path}_{camera}_{datetime.today().strftime("%Y%m%d_%H%M%S")}'

	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOn(camera, real_path))
		time.sleep(0.01)


def stop(camera):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOff(camera))
		time.sleep(0.01)


