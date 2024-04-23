from actions.line_movement import line_movement
from actions.stab_new import stab
from actions.tack import tack
from actions import detection
from actions import photosave

from base.network import Net
from base.message import InitRobot


Net().send(InitRobot(yaw=0, depth=0, x=0, y=0))

photosave.start("Bottom", 'line')

tack(mode="Absolute", yaw=0, speed=0.3, depth=0.5, dist=0.5)

detection.on(obj="Aruco", timeout=30)

line_movement(0.25, 3, depth=0.5, timeout=60)

stab(origin="Aruco", yaw=None, dt=6, depth=0.5)
stab(origin="Aruco", yaw="Object", dt=6, depth=0.5)
stab(origin="Aruco", yaw="Object", dt=15, depth=1.2)

photosave.stop("Bottom")
