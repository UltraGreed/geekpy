#!python3 test_square.py
import sys, setproctitle
sys.path.append('../actions')
from move_yaw import move_yaw
setproctitle.setproctitle(sys.argv[0])  # Set filename.py title for process.

print   ("Square trajectory task started...")

move_yaw(origin='Navigation', yaw=  0, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw= 90, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=180, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=270, dist=4.0, speed=0.5, depth=0.0)

move_yaw(origin='Navigation', yaw=  0, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw= 90, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=180, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=270, dist=4.0, speed=0.5, depth=0.0)

move_yaw(origin='Navigation', yaw=  0, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw= 90, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=180, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=270, dist=4.0, speed=0.5, depth=0.0)

move_yaw(origin='Navigation', yaw=  0, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw= 90, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=180, dist=4.0, speed=0.5, depth=0.0)
move_yaw(origin='Navigation', yaw=270, dist=4.0, speed=0.5, depth=0.0)

print   ("Task end.")
