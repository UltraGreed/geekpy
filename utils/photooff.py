#!/usr/bin/python
from base import message, network


net = network.Net()

msg = message.PhotoOff(camera='Bottom')
net.send(msg)
