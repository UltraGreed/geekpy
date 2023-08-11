#!python3
### DO IT ONCE IN CONSOLE: export PYTHONPATH=$(realpath ..)
import sys, setproctitle
from actions.tack import tack
from actions.stab import stab
from actions.goto import goto
from actions import photosave
from actions import detection
from actions import key
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
print(' '.join(sys.argv), "end!")
