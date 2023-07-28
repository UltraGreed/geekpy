#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.tack import tack
from actions.stab import stab
from actions.goto import goto
from actions import photosave
from actions import detection
from actions import key
setproctitle.setproctitle(' '.join(sys.argv))

print(' '.join(sys.argv), "begin...")
tack(origin='Navigation', yaw=-45, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Navigation', yaw=-45, dist=2.0, speed=0.3, dt=10.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Current', yaw=-90, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
tack(origin='Navigation', yaw=-45, dist=1.0, speed=0.3, dt=5.0, depth=0.5)
photosave.start(camera='Front', path=' '.join(sys.argv))
detection.on(obj='BallY')
goto(origin='BallY', radius=0.3, speed=0.3, hold_time=0.0, depth=0.5)
detection.off(obj='BallY')
goto(origin='Cells', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
stab(origin='Current', yaw=0.0, dt=5.0, depth=0.5)
detection.on(obj='CellY')
goto(origin='CellY', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
stab(origin='CellY', right=0.035, front=-0.065, yaw=0.0, dt=10.0, depth=0.5)
key.on(key='Right', hold_time=1.0)
stab(origin='CellY', right=-0.035, front=-0.065, yaw=0.0, dt=10.0, depth=0.5)
key.on(key='Left', hold_time=1.0)
detection.off(obj='CellY')
tack(origin='Navigation', yaw=45, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
goto(origin='Frame', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
stab(origin='Current', yaw=90.0, dt=10.0, depth=0.5)
stab(origin='Current', yaw=90.0, dt=10.0, depth=0.0)
stab(origin='Current', yaw=90.0, dt=10.0, depth=0.5)
tack(origin='Navigation', yaw=90.0, dist=2.0, speed=0.3, dt=10.0, depth=0.5)
print(' '.join(sys.argv), "end!")
