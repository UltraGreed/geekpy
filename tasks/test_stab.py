import sys
import setproctitle

from actions.stab import stab

from base import network
from base.message import InitRobot


setproctitle.setproctitle(' '.join(sys.argv))

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')

network.Net().send(InitRobot(yaw=0, depth=0))

stab(origin='Line', yaw=0, front=0.0, right=0.0, dt=120.0, depth=0.5)

print(' '.join(sys.argv), "end!")
