from actions.line_movement import line_movement
from actions.stab import stab
# from actions.tack import tack
from actions import detection
from actions import photosave
from actions.tack import tack

from base.network import Net
from base.message import InitRobot


Net().send(InitRobot(yaw=0, depth=0, x=0, y=0))

photosave.start("Bottom", 'line_sim')

# tack(mode="Absolute", yaw=0, speed=0.3, depth=0.0, dist=0.5)

# detection.on(obj="Aruco", timeout=30)

line_movement(speed=0.2, exit_object='SquareGreen', object_delay=40, depth=0.75, timeout=90)

# stab(origin="Aruco", yaw=None, dt=6, depth=0.35)
# stab(origin="Aruco", yaw="Object", dt=6, depth=0.35)
# stab(origin="Aruco", yaw="Object", dt=20, depth=1.3)

photosave.stop("Bottom")
