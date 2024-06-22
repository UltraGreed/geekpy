import time

from base import message, network
from base.timer import Timer


def init_robot(**kwargs):
    net = network.Net()

    timer = Timer(0.05)
    while not timer.is_unlock:
        net.send(message.InitRobot(**kwargs))
        time.sleep(0.01)
