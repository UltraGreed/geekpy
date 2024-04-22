from actions.line_movement import line_movement
from actions.stab_new import stab
from actions.tack import tack
from actions import detection

from base.network import Net
from base.message import InitRobot


Net().send(InitRobot(yaw=0, depth=0, x=0, y=0))

# tack(mode="Absolute", yaw=0, speed=0.3, depth=0.5, dist=0.5)

detection.on(obj="Aruco", timeout=30)

line_movement(0.2, 5, depth=0.5, timeout=30)

stab(origin="Aruco", yaw=None, dt=10, depth=0.5)
stab(origin="Aruco", yaw="Object", dt=10, depth=0.5)
stab(origin="Aruco", yaw="Object", dt=8, depth=1.2)
