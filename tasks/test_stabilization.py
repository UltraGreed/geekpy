#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.stab_xy import stab_xy
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Stab Red ball for 30 sec...")
stab_xy (origin='BallR', x=0.0,  y=0.0, yaw=None, dt=30.0, depth=None)
print(' '.join(sys.argv), "end!")
