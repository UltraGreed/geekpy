#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.tack import tack
from actions.stab import stab
from actions.goto import goto
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Move to Cells...");    goto(origin='CellB', radius=1.0,   speed=0.5,         depth=0.2)
print("Stab Blue Cell...");   stab(origin='CellB', x=0.0, y=0.0, left=0.1, front=-0.05, yaw=0.0, dt=60.0, depth=None)
print(' '.join(sys.argv), "end!")

