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

tack(mode="Absolute", has_target=True, yaw=0, speed=0, depth=0.4, dist=None, dt=40)

print(' '.join(sys.argv), "end!")

