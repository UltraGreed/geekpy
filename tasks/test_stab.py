import sys
import setproctitle

sys.path.append('./')

from actions.aruco_stab import aruco_stab
from actions import detection

from base import network
from base.message import InitRobot


setproctitle.setproctitle(' '.join(sys.argv))

net = network.Net()

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')

net.send(InitRobot(yaw=0, depth=0))

detection.on(obj="Aruco")

aruco_stab(front=0.0, right=0.0, dt=120.0, depth=0.5)

print(' '.join(sys.argv), "end!")
