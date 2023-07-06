#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.move_yaw import move_yaw
from actions.stab_xy import stab_xy
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Move to all balls in navigation mode...")
move_yaw(origin='Navigation', yaw=-45, dist=4.0, speed=0.5, depth=0.0)
print("Stabilize red ball...")
stab_xy (origin='BallR', x=0.0,  y=0.0, yaw=None, dt=20.0, depth=None)
print("Stabilize yellow ball...")
stab_xy (origin='BallY', x=0.0,  y=0.0, yaw=None, dt=20.0, depth=None)
print("Stabilize green ball...")
stab_xy (origin='BallG', x=0.0,  y=0.0, yaw=None, dt=20.0, depth=None)
print(' '.join(sys.argv), "end!")
