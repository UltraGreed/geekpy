import time
import sys

sys.path.append("./")
from base import network, message


TIMER = 1 / 12

net = network.Net()
net.send(message.InitRobot(yaw=0, depth=0))
msg = message.Tack(stab_depth=0.5,speed_x=0.2)

timeout = 5.0

start = time.time()

while time.time() - start < timeout:
    net.send(msg)
    time.sleep(TIMER)

