import time
import sys

sys.path.append("./")

from base import message
from base import network

net = network.Net()
msg = message.Tack(speed_y=0.1)

SEC = 1.0
start = time.time()
while time.time() - start < SEC:
    net.send(msg)
