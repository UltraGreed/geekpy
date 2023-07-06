#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.move_object import move_object
# from actions.move_yaw import move_yaw
# from actions.stab_xy import stab_xy
# from actions.stab_xy import stab_xy
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Arrive to balls...")
move_object(origin='BallG', radius=1.0, speed=0.5, depth=None)
print("Arrive to cells...")
move_object(origin='CellR', radius=1.0, speed=0.5, depth=None)
print("Arrive to frame...")
move_object(origin='Frame', radius=1.0, speed=0.5, depth=None)
print(' '.join(sys.argv), "end!")
