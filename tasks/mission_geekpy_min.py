from actions.line_movement import line_movement
from actions.stab import stab
from actions.goto import goto
from actions import photosave
from actions.tack import tack
from actions.object_reaction_min import object_reaction_min
from actions.init_robot import init_robot

import multiprocessing
import time

mission_depth = 1.3

init_robot(yaw=0, depth=0, x=0, y=0)

# detection.on('Pinger', 30)

photosave.start("Bottom", None)

# I know you won't like this,
# but I really prefer this way of doing things :)
# Basically all you have to do is start it like
# in this example and then terminate at the end.
object_reaction_process = multiprocessing.Process(
    target=object_reaction_min,
    kwargs={
        'object_order': ('square',
                         'square',
                         'triangle',
                         'triangle'),
        'object_interval': 5,
        'object_green_led': 'SquareOrange',
        'object_red_led': 'SquareBlack',
        'ball_drop_delay': 2,
        'orange_count': 4
    }
)
object_reaction_process.start()

time1 = time.time()
line_movement(exit_object='SquareGreen', object_delay=50, exit_delay=2,
              timeout=60, speed=0.2, depth=mission_depth)

print(f"Line ended in ${time.time() - time1}")

tack(mode="Absolute", yaw=260, speed=0, depth=mission_depth, dt=5)

tack(mode="Absolute", yaw=260, speed=0.5, depth=mission_depth, dist=2)

goto(origin="Pinger", speed=0.2, radius=1, hold_time=5, depth=mission_depth)

stab(origin="Pinger", yaw=90, depth=mission_depth, dt=5)

photosave.stop("Bottom")

# Don't forget to terminate started processes
object_reaction_process.terminate()
