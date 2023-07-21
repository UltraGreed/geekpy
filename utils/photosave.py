#!/usr/bin/python
from base import message, network


net = network.Net()

msg = message.PhotoSave(camera='Bottom', folder='bw_test_bottom')
net.send(msg)

# msg = message.PhotoSave(camera='Front', folder='bw_test_front')
# net.send(msg)
