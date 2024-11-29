from actions.line_movement import line_movement
from actions.stab import stab
from actions.goto import goto
from actions import photosave
from actions.tack import tack
from actions import detection
from actions.object_reaction_akva24 import object_reaction_akva24
from actions.init_robot import init_robot

import multiprocessing
import time


mission_depth = 1.0
pool_depth = 2.0

lower_depth = 1.1
upper_depth = 0.6
start_depth = lower_depth

init_robot(yaw=0, depth=0, x=0, y=0)

photosave.start("Bottom", None)

detection.on("GreenTriangle")
detection.on("YellowSquare")
detection.on("RedSircle")

stab(origin="RedSircle", yaw=0.0, dt=5.0, depth=start_depth)

object_reaction_process = multiprocessing.Process(
    target=object_reaction_akva24,
    kwargs={
        "object_down" : "GreenTriangle",
        "object_up" : "YellowSquare",
        "lower_depth": lower_depth,
        "upper_depth": upper_depth,
        "start_depth": start_depth,
    }
)
object_reaction_process.start()

time1 = time.time()
line_movement(exit_object="Target", object_delay=30, exit_delay=2,
              timeout=140, speed=0.2)

print(f"Line ended in ${time.time() - time1}")

# tack(mode="Absolute", yaw=260, speed=0, depth=mission_depth, dt=5)

# tack(mode="Absolute", yaw=260, speed=0.5, depth=mission_depth, dist=3)

# goto(origin="Pinger", speed=0.2, radius=1, hold_time=5, depth=mission_depth)

# stab(origin="Pinger", yaw=90, depth=mission_depth, dt=5)

photosave.stop("Bottom")

# Don't forget to terminate started processes
object_reaction_process.terminate()
