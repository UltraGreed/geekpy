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

print('set yaw to gate...')
tack(origin='Navigation', yaw=-45, dist=1.0, speed=0.0, dt=5.0, depth=0.5)

print('tack to gate...')
tack(origin='Current', yaw=0.0, dist=3.0, speed=0.3, dt=20.0, depth=0.5)

# print('720 degree rotate...')
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# tack(origin='Current', yaw=90.0, dist=1.0, speed=0.0, dt=5.0, depth=0.5)

print('tack to balls...')
detection.on(obj='BallY', timeout=2.0)
tack(origin='Current', yaw=0.0, dist=4.7, speed=0.3, dt=20.0, depth=0.5)
goto(origin='BallY', radius=0.3, speed=0.3, hold_time=0.0, depth=0.5)
detection.off(obj='BallY', timeout=0.0)

print('tack to cells...')
tack(origin='Cells', dist=4.0, speed=0.3, dt=15.0, depth=5.0)
detection.on(obj='Cells', timeout=2.0)
goto(origin='Cells', radius=0.3, speed=0.3, hold_time=0.0, depth=0.5)
stab(origin='Cells', yaw=0.0, dt=10.0, depth=0.5)
detection.off(obj='Cells', timeout=0.0)

print('tack to red cells...')
detection.on(obj='CellR', timeout=10.0)
tack(origin='Current', yaw=0.0, dist=1.5, speed=0.3, dt=10.0, depth=0.5)
stab(origin='CellR', right=0.035, front=-0.065, dt=15.0, depth=0.5)

print('drop into red cells...')
key.on(key='Right', hold_time=1.0)
stab(origin='CellR', right=-0.035, front=-0.065, dt=15.0, depth=0.5)
key.on(key='Left', hold_time=1.0)
detection.off(obj='CellR', timeout=0.0)

print('tack to frame')
tack(origin='Current', yaw=90.0, dist=3.0, speed=0.3, dt=15.0, depth=0.5)

# photosave.start(camera='Front', path=' '.join(sys.argv))
# detection.on(obj='BallY')
# goto(origin='BallY', radius=0.3, speed=0.3, hold_time=0.0, depth=0.5)
# detection.off(obj='BallY')
# detection.on(obj='Cells')
# goto(origin='Cells', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
# detection.off(obj='Cells')
# stab(origin='Current', yaw=0.0, dt=5.0, depth=0.5)
# detection.on(obj='CellY')
# goto(origin='CellY', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
# stab(origin='CellY', right=0.035, front=-0.065, yaw=0.0, dt=10.0, depth=0.5)
# key.on(key='Right', hold_time=1.0)
# stab(origin='CellY', right=-0.035, front=-0.065, yaw=0.0, dt=10.0, depth=0.5)
# key.on(key='Left', hold_time=1.0)
# detection.off(obj='CellY')
# tack(origin='Navigation', yaw=45, dist=1.0, speed=0.0, dt=5.0, depth=0.5)
# goto(origin='Frame', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
# stab(origin='Current', yaw=90.0, dt=10.0, depth=0.5)
# stab(origin='Current', yaw=90.0, dt=10.0, depth=0.0)
# stab(origin='Current', yaw=90.0, dt=10.0, depth=0.5)
# tack(origin='Navigation', yaw=90.0, dist=2.0, speed=0.3, dt=10.0, depth=0.5)


# tack(origin='Current', yaw=0.0, dist=2.0, speed=0.3, dt=15.0, depth=0.5)
# detection.on(obj='BallY')
# goto(origin='BallY', radius=0.3, speed=0.3, hold_time=0.0, depth=0.5)
# detection.off(obj='BallY')
# detection.on(obj='Cells')
# goto(origin='Cells', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
# detection.off(obj='Cells')
# stab(origin='Current', yaw=0.0, dt=5.0, depth=0.5)
# detection.on(obj='CellR')
# goto(origin='CellR', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
# stab(origin='CellR', right=0.035, front=-0.065, yaw=0.0, dt=10.0, depth=0.5)
# key.on(key='Right', hold_time=1.0)
# stab(origin='CellR', right=-0.035, front=-0.065, yaw=0.0, dt=10.0, depth=0.5)
# key.on(key='Left', hold_time=1.0)
# detection.off(obj='CellR')
# tack(origin='Navigation', yaw=-90, dist=2.0, speed=0.0, dt=5.0, depth=0.5)
# # goto(origin='Frame', radius=0.5, speed=0.3, hold_time=5.0, depth=0.5)
# stab(origin='Current', yaw=90.0, dt=10.0, depth=0.5)
# stab(origin='Current', yaw=90.0, dt=10.0, depth=0.0)
# stab(origin='Current', yaw=90.0, dt=10.0, depth=0.5)
# tack(origin='Navigation', yaw=90.0, dist=2.0, speed=0.3, dt=10.0, depth=0.5)


print(' '.join(sys.argv), "end!")
