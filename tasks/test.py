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

tack(mode='Absolute', yaw=0.0, dist=0, speed=0, depth=0.5, dt=10)
# tack(mode='Absolute', yaw=0.0, dist=2.0, speed=0.3, depth=0.5)
# tack(mode='Absolute', yaw=180, dist=0.0, speed=0.0, depth=0.5, dt=3)
# tack(mode='Absolute', yaw=180, dist=2.0, speed=0.3, depth=0.5)

print(' '.join(sys.argv), "end!")
