from actions.line_movement import line_movement
from actions import photosave
from actions.init_robot import init_robot
from actions.target_homing import target_homing

import multiprocessing
import time


mission_depth = 0.5
pool_depth = 1.15

lower_depth = 0.25
upper_depth = 0
target_depth = lower_depth

line_speed = 0.2
homing_speed = 0.1

line_segments = [
#    depth      time
    (lower_depth, 10),
    (upper_depth, 20),
]

init_robot(yaw=0, depth=0, x=0, y=0)

photosave.start("Bottom", None)
photosave.start("Front", None)

target_homing_process = multiprocessing.Process(
    target=target_homing,
    kwargs={
        "speed": homing_speed,
        "depth": target_depth,
    },
)

time1 = time.time()
for i, (depth, timeout) in enumerate(line_segments):
    if i == len(line_segments) - 1:
        target_homing_process.start()

    line_movement(
        exit_object="NOEXIT",
        object_delay=-1,
        exit_delay=-1,
        timeout=timeout,
        depth=depth,
        speed=line_speed,
    )

photosave.stop("Bottom")
photosave.stop("Front")

# Don't forget to terminate started processes
target_homing_process.terminate()
print(f"Line ended in ${time.time() - time1}")
