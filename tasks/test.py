#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys
import setproctitle

from actions.tack import tack

from base import network
from base.message import InitRobot


setproctitle.setproctitle(' '.join(sys.argv))

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')

network.Net().send(InitRobot(yaw=0, depth=0))

tack(origin='Navigation', yaw=0.0, dist=1.0, speed=0.0, depth=0.5)
tack(origin='Navigation', yaw=-30, dist=1.0, speed=0.0, depth=0.5, dt=3)
tack(origin='Navigation', yaw=-30, dist=1.0, speed=0.0, depth=0.5, dt=3)
tack(origin='Navigation', yaw=0.0, dist=1.0, speed=0.0, depth=0)

print(' '.join(sys.argv), "end!")
