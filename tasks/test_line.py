from actions.line_movement import line_movement
from actions.stab import stab
from actions.goto import goto
from actions import photosave
from actions.tack import tack
from actions.object_reaction_max import object_reaction_max
from actions.init_robot import init_robot

import multiprocessing
import time


mission_depth = 0.4
pool_depth = 1.2

init_robot(yaw=0, depth=0, x=0, y=0)

photosave.start("Bottom", None)

# I know you won't like this,
# but I really prefer this way of doing things :)
# Basically all you have to do is start it like
# in this example and then terminate at the end.
# object_reaction_process = multiprocessing.Process(
#     target=object_reaction_max,
#     kwargs={
#         'object_order': ('square',
#                          'square',
#                          'triangle',
#                          'triangle'),
#         'object_interval': 5,
#         'object_green_led': 'SquareOrange',
#         'object_red_led': 'SquareBlack',
#         'ball_drop_delay': 2,
#         'line_depth': mission_depth,
#         'max_depth': pool_depth,
#         'orange_count': 4
#     }
# )
# object_reaction_process.start()
#
time1 = time.time()
line_movement(exit_object='DONTEXIT', object_delay=70, exit_delay=20,
              timeout=20, speed=0.2, depth=mission_depth)

print(f"Line ended in ${time.time() - time1}")

photosave.stop("Bottom")

# Don't forget to terminate started processes
# object_reaction_process.terminate()
