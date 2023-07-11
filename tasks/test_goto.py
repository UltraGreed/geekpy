#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.goto import goto
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Goto to Green Ball..."); goto(origin='BallG', radius=1.0, speed=0.5, depth=None)
print("Goto to Red Cell...");   goto(origin='CellR', radius=1.0, speed=0.5, depth=None)
print("Goto to Frame...");      goto(origin='Frame', radius=1.0, speed=0.5, depth=None)
print(' '.join(sys.argv), "end!")
