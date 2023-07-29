# Это сообщение DetectionOn/Off примет модуль сцены и
# либо начнет применять результаты распознавания, либо их игнорить.
import sys
import time

sys.path.append('./')
from base import message, network
from base.timer import Timer


def on(obj, timeout=10.0):
	net = network.Net()

	timer = Timer(0.05)
	while not timer.is_unlock:
		net.send(message.DetectionOn(obj, timeout))
		time.sleep(0.001)


def off(obj, timeout=10.0):
	net = network.Net()

	timer = Timer(0.05)
	while not timer.is_unlock:
		net.send(message.DetectionOff(obj, timeout))
		time.sleep(0.001)
