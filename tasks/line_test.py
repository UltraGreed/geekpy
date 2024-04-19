from actions.line_movement import line_movement

from base.network import Net
from base.message import InitRobot


Net().send(InitRobot(yaw=0, depth=0))

line_movement(0.1, depth=0.5, timeout=180)
