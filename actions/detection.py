# Это сообщение DetectionOn/Off примет модуль сцены и
# либо начнет применять результаты распознавания, либо их игнорить.
import sys
import time

sys.path.append('./')
from base import message, network
from base.timer import Timer


def detection_on(obj):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.DetectionOn(obj))
		time.sleep(0.01)


def detection_off(obj):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.DetectionOff(obj))
		time.sleep(0.01)
