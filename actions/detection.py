# Это сообщение DetectionOn/Off примет модуль сцены и
# либо начнет применять результаты распознавания, либо их игнорить.
import sys
import time

sys.path.append('./')
from base import message, network
from base.timer import Timer


def on(obj):
	net = network.Net()

	timer = Timer(0.5)
	while not timer.is_unlock:
		net.send(message.DetectionOn(obj))
		time.sleep(0.01)


def off(obj):
	net = network.Net()

	timer = Timer(0.5)
	while not timer.is_unlock:
		net.send(message.DetectionOff(obj))
		time.sleep(0.01)
