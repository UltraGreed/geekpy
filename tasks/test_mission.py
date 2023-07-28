#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.tack import tack
from actions.stab import stab
from actions.goto import goto
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
# goto(origin='BallR', radius=1.0, speed=0.1, hold_time=5, depth=None)
# tack(origin='Current', yaw=0, dist=4.0, speed=0.3, dt=10.0, depth=None)
# tack(origin='Navigation', yaw=-90, dist=4.0, speed=0.3, dt=60.0, depth=None)
# tack(origin='BallR', yaw=None, dist=None, speed=0.3, dt=10.0, depth=None)
# goto(origin='BallR', radius=0.5, speed=0.3, depth=None)
# stab(origin='BallR', right=0.035, front=-0.065, yaw=None, dt=10.0)
# stab(origin='BallR', right=-0.035, front=-0.065, yaw=None, dt=10.0)
# stab(origin='Current', x=0.0, y=3.0, right=-0.035, front=-0.065, yaw=None, dt=1000.0)
# stab(origin='Navigation', x=1.0, y=1.0, right=-0.035, front=-0.065, yaw=None, dt=1000.0)
print(' '.join(sys.argv), "end!")
