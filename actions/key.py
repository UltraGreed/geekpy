import sys
import time

sys.path.append('./')
from base import message, network
from base.timer import Timer


def key_on(key, hold_time):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.KeyOn(key, hold_time))
		time.sleep(0.01)


def key_off(key):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.KeyOff(key))
		time.sleep(0.01)

