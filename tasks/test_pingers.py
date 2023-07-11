#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.move_yaw    import move_yaw
from actions.stab_xy     import stab_xy
from actions.move_object import move_object
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
print("Move to Cells..."); move_object(origin='Cells', radius=0.5, speed=0.5, depth=0.2)
print("Stab Cells...");    stab_xy    (origin='Cells', x=0.0, y=0.0, yaw=0.0, dt=30.0, depth=0.2)
print("Move to Frame..."); move_object(origin='Frame', radius=0.5, speed=0.5, depth=0.2)
print("Stab Frame...");    stab_xy    (origin='Frame', x=0.0, y=0.0, yaw=0.0, dt=30.0, depth=0.2)
print(' '.join(sys.argv), "end!")

