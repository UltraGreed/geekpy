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


tack(mode='Absolute', yaw=0.0, dist=0.5, speed=0.2, depth=0.3)
tack(mode='Absolute', yaw=0.0, dist=5.0, speed=0.8, depth=0.3)
photosave.start('Front', 'aquarobotech')
tack(mode='Absolute', yaw=0.0, dist=2.3, speed=0.4, depth=0.20, has_target=True)
photosave.stop('Front')
tack(mode='Absolute', yaw=0.0, dist=0.75, speed=-0.2, depth=0.175)
tack(mode='Absolute', yaw=0.0, dist=1.0, speed=0, depth=0, dt=2)

print(' '.join(sys.argv), "end!")
