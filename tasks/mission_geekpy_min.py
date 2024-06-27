from actions.line_movement import line_movement
from actions.stab import stab
# from actions.tack import tack
from actions import detection
from actions.goto import goto
from actions import photosave
from actions.tack import tack
from actions.object_reaction_min import object_reaction_min
from actions.init_robot import init_robot

import multiprocessing

line_depth = 0.6
max_depth = 1.2


init_robot(yaw=0, depth=0, x=0, y=0)

photosave.start("Bottom", 'line_sim')

# I know you won't like this,
# but I really prefer this way of doing things :)
# Basically all you have to do is start it like
# in this example and then terminate at the end.
object_reaction_process = multiprocessing.Process(
    target=object_reaction_min,
    args=(('triangle',
           'triangle',
           'square',
           'square'),
          5,
          'SquareYellow',
          'SquareBlack',
          0,
          line_depth,
          max_depth)
)
object_reaction_process.start()

line_movement(exit_object='SquareGreen', object_delay=40, exit_delay=5, timeout=90, speed=0.15, depth=line_depth)

tack(mode="Absolute", yaw=18, speed=0, depth=1, dt=5)

goto(origin="Boxes", speed=0.2, radius=1, hold_time=5, depth=1)

tack(mode="Absolute", yaw=77, speed=0, depth=1, dt=5)

tack(mode="Relative", yaw=0, speed=0.2, depth=1, dist=1)

photosave.stop("Bottom")

# Don't forget to terminate started processes
object_reaction_process.terminate()
