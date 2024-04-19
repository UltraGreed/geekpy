import time
import sys

sys.path.append("./")
from base import network, message


TIMER = 1 / 12

net = network.Net()
msg = message.Tack(speed_y=0.5)

timeout = 5.0

start = time.time()

while time.time() - start < timeout:
    net.send(msg)
    time.sleep(TIMER)

