import sys
import setproctitle

sys.path.append('./')

from actions.tack import tack

from base import network
from base.message import InitRobot


setproctitle.setproctitle(' '.join(sys.argv))

net = network.Net()

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')

net.send(InitRobot(yaw=0, depth=0))

tack(mode="Absolute", yaw=0, speed=0, depth=0.5, dist=None, dt=10)
tack(mode="Absolute", yaw=170, speed=0, depth=0.5, dist=None, dt=10)
tack(mode="Absolute", yaw=0, speed=0, depth=0.5, dist=None, dt=10)

print(' '.join(sys.argv), "end!")
