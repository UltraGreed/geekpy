from actions.line_movement import line_movement
from actions import photosave
from actions.init_robot import init_robot
from actions.target_homing import target_homing

import multiprocessing
import time


mission_depth = 0.75
pool_depth = 2.0

lower_depth = 1.1
upper_depth = 0.6
target_depth = lower_depth

line_speed = 0.2
homing_speed = 0.1

init_robot(yaw=0, depth=0, x=0, y=0)

photosave.start("Bottom", None)
photosave.start("Front", None)

target_homing_process = multiprocessing.Process(
    target=target_homing,
    kwargs={
        "speed" : homing_speed,
        "depth": target_depth,
    }
)
target_homing_process.start()

time1 = time.time()
line_movement(exit_object="NOEXIT", object_delay=-1, exit_delay=-1,
              timeout=100, speed=line_speed, depth=mission_depth)

print(f"Line ended in ${time.time() - time1}")

photosave.stop("Bottom")
photosave.stop("Front")

# Don't forget to terminate started processes
target_homing_process.terminate()
