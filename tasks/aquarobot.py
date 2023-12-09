#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import setproctitle
import sys

from actions import photosave
from actions.tack import tack
from base import network
from base.message import InitRobot

setproctitle.setproctitle(' '.join(sys.argv))

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')

network.Net().send(InitRobot(yaw=0, depth=0))

tack(origin='Navigation', yaw=0.0, dist=0.5, speed=0.4, depth=0.4)
photosave.start('Front', 'aquarobotech')
tack(origin='Navigation', yaw=0.0, dist=3.5, speed=0.6, depth=0.4)
tack(origin='Navigation', yaw=0.0, dist=4.0, speed=0.6, depth=0.4, has_target=True)
photosave.stop('Front')
tack(origin='Navigation', yaw=0.0, dist=1.0, speed=-0.1, depth=0, dt=2)

print(' '.join(sys.argv), "end!")
