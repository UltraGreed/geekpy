from actions.line_movement import line_movement
from actions import photosave
from actions.init_robot import init_robot
from actions.target_homing import target_homing
from actions import key
from actions.tack import tack

import time


pool_depth = 1

lower_depth = 0.55
upper_depth = -0.1
target_depth = 0.45

line_speed = 0.35
homing_speed = 0.1

line_segments = [
#    depth       time
    (lower_depth, 10),
    (lower_depth, 10),
    (upper_depth, 6),
]

photosave.start("Bottom", None)
photosave.start("Front", None)

time1 = time.time()
line_movement(
    exit_object="NOEXIT",
    object_delay=-1,
    exit_delay=-1,
    timeout=10,
    depth=lower_depth,
    speed=line_speed,
)
line_movement(
    exit_object="NOEXIT",
    object_delay=-1,
    exit_delay=-1,
    timeout=10,
    depth=lower_depth,
    speed=line_speed,
)
line_movement(
    exit_object="NOEXIT",
    object_delay=-1,
    exit_delay=-1,
    timeout=10,
    depth=upper_depth,
    speed=0.15,
)
key.on('Red', 10)
target_homing(
    speed=homing_speed,
    depth=target_depth,
    timeout=15
)
key.on('Green', 7)
tack(mode='Relative', yaw=0.0, dt=7, speed=-0.2, depth=target_depth)

photosave.stop("Bottom")
photosave.stop("Front")

# Don't forget to terminate started processes
print(f"Line ended in ${time.time() - time1}")
