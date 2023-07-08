#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.move_yaw import move_yaw
from actions.stab_xy import stab_xy
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Move to Frame with current yaw...")
move_yaw(origin='Current', yaw=0, dist=10.0, speed=0.5, depth=0.0)
print("Stabilize Frame...")
stab_xy (origin='Frame', x=0.0,  y=0.0, yaw=None, dt=40.0, depth=None)
print(' '.join(sys.argv), "end!")
