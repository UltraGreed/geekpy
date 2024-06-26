import sys
import setproctitle

from actions.tack import tack

from base import network
from base.message import InitRobot

sys.path.append('./')


setproctitle.setproctitle(' '.join(sys.argv))

net = network.Net()

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')

net.send(InitRobot(yaw=0, depth=0, x=0, y=0))

tack(mode='Absolute', yaw=0.0, dist=0, speed=0, depth=0.5, dt=30)

print(' '.join(sys.argv), "end!")
