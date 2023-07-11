#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.tack import tack
from actions.stab import stab
from actions.goto import goto
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Move to Cells...");    goto(origin='Cells', radius=0.5,   speed=0.5,         depth=0.2)
print("Stab Cells...");       stab(origin='Cells', x=0.0, y=0.0, yaw=0.0,  dt=10.0, depth=0.2)
print("Stab Blue Cell...");   stab(origin='CellB', x=0.0, y=0.0, yaw=None, dt=20.0, depth=None)
print("Stab Yellow Cell..."); stab(origin='CellY', x=0.0, y=0.0, yaw=None, dt=20.0, depth=None)
print("Stab Red Cell...");    stab(origin='CellR', x=0.0, y=0.0, yaw=None, dt=20.0, depth=None)
print("Move to Frame...");    goto(origin='Frame', radius=0.5,   speed=0.5,         depth=0.2)
print("Stab Frame...");       stab(origin='Frame', x=0.0, y=0.0, yaw=0.0,  dt=20.0, depth=0.2)
print(' '.join(sys.argv), "end!")

