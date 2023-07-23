# @todo: Нужно заполнить функции, которые включают и выключают камеры.
# Особенность в том, что сообщения могут теряться,
# поэтому нужно в цикле длительностью 0.5 сек с периодом 0.01 сек
# отправить соответствующее сообщение.
# Папка сохранения фоток пусть именуется "[path]_[bottom|front]_DAY_HH-MM-SS"
import sys
import time

sys.path.append('./')
from base import message, network
from base.timer import Timer


def startPhotosave(camera, path):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOn(camera, path))
		time.sleep(0.01)


def stopPhotosave(camera):
	net = network.Net()
	timer = Timer(0.5)
	while True:
		if timer.is_unlock:
			break

		net.send(message.PhotoOff(camera))
		time.sleep(0.01)


