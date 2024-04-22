import sys
import setproctitle

sys.path.append('./')

from actions.stab_new import stab
from actions import detection

from base import network
from base.message import InitRobot


setproctitle.setproctitle(' '.join(sys.argv))

net = network.Net()

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')

net.send(InitRobot(yaw=0, depth=0))

detection.on(obj="Aruco", timeout=30)

stab(origin="Aruco", yaw="Object", dt=10.0, depth=0.5)
stab(origin="Aruco", yaw="Object", dt=10.0, depth=1.2)

print(' '.join(sys.argv), "end!")
