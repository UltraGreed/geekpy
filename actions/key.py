import sys
import time

sys.path.append('./')
from base import message, network
from base.timer import Timer


def on(key, hold_time):
	net = network.Net()

	timer = Timer(0.05)
	while not timer.is_unlock:
		net.send(message.KeyOn(key, hold_time))
		time.sleep(0.01)


def off(key):
	net = network.Net()

	timer = Timer(0.05)
	while not timer.is_unlock:
		net.send(message.KeyOff(key))
		time.sleep(0.01)
