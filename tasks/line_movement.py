from actions.line_movement import line_movement
from actions.stab import stab
# from actions.tack import tack
from actions import detection
from actions import photosave

from base.network import Net
from base.message import InitRobot


Net().send(InitRobot(yaw=0, depth=0, x=0, y=0))

photosave.start("Bottom", 'line_task')

# tack(mode="Absolute", yaw=0, speed=0.3, depth=0.0, dist=0.5)

detection.on(obj="Aruco", timeout=30)

line_movement(speed=0.2, aruco_delay=3, depth=0.0, timeout=90)

stab(origin="Aruco", yaw=None, dt=6, depth=0.3)
stab(origin="Aruco", yaw="Object", dt=6, depth=0.3)
stab(origin="Aruco", yaw="Object", dt=15, depth=1.3)

photosave.stop("Bottom")
