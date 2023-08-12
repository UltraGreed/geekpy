#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle, time
from actions.tack import tack
from actions.stab import stab
from actions.goto import goto
from actions import photosave
from actions import detection
from actions import key
from actions.loop import loop
from base.message import DEPTH
setproctitle.setproctitle(' '.join(sys.argv))

task_name = ' '.join(sys.argv)

print(task_name, 'begin...')
print('start photosave...')
photosave.start(camera='Bottom', path='test_mission')
photosave.start(camera='Front', path='test_mission')

print('detection off...')
detection.off(obj='BallY', timeout=0.0)
detection.off(obj='BallR', timeout=0.0)
detection.off(obj='BallG', timeout=0.0)
detection.off(obj='Cells', timeout=0.0)
detection.off(obj='CellB', timeout=0.0)
detection.off(obj='CellY', timeout=0.0)
detection.off(obj='CellR', timeout=0.0)
detection.off(obj='Frame', timeout=0.0)

print('gate')
tack(origin='Current', yaw=0.0, dist=2.0, speed=0.7, depth=1.1)
loop(roll=1000000, dt=3.5)
tack(origin='Navigation', yaw=1.0, dist=0.75, speed=0.7, depth=0.7)
tack(origin='Navigation', yaw=-95.0, dist=15.0, speed=0.7, depth=0.4)

CORRECTION = 15.0

print('cells')
detection.on(obj='Cells', timeout=10.0)
goto(origin='Cells', radius=1.0, speed=0.4, hold_time=4.0, depth=0.5)
stab(origin='Cells', yaw=CORRECTION, dt=10.0, depth=0.5)
detection.off(obj='Cells', timeout=100.0)
tack(origin='Navigation', yaw=CORRECTION, dist=1.2, speed=0.4, dt=4.0, depth=0.5)

print('drop')
detection.on(obj='CellY', timeout=10.0)
tack(origin='Navigation', yaw=CORRECTION, dist=1.0, speed=0.4, dt=4.0, depth=0.5)
stab(origin='CellY', yaw=CORRECTION, front=-0.065, right=0.035, dt=10.0, depth=1.1)
key.on(key='Right', hold_time=1.0)
# stab(origin='CellR', yaw=CORRECTION, front=-0.065, right=-0.035, dt=10.0, depth=1.0)
# key.on(key='Left', hold_time=1.0)
tack(origin='Current', dist=1.0, speed=0.0, yaw=0.0, dt=3.0, depth=1.1)
detection.off(obj='CellY', timeout=100.0)

print('frame')
detection.on(obj='Frame', timeout=10.0)
tack(origin='Current', dist=1.0, speed=0.0, yaw=0.0, dt=5.0, depth=0.5)
goto(origin='Frame', radius=1.0, speed=0.4, hold_time=8.0, depth=0.5)
time.sleep(7.0)
# stab(origin='Frame', dt=5.0, depth=0.5)
# stab(origin='Frame', dt=8.0, depth=None)
stab(origin='Frame', dt=5.0, depth=0.5)

print('get back')
tack(origin='Navigation', yaw=-180.0, speed=0.6, dist=3.0, depth=0.5)

print(' '.join(sys.argv), "end!")
