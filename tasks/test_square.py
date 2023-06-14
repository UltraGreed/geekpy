#!python3 test_square.py
import sys
sys.path.append('../actions')
from ahead import ahead

# Test square trajectory.
print("Start task")
ahead(origin = 'Navigation', yaw =   0, dist = 3, speed = 0.5, depth = 0.0)
print("Task #1 done")
ahead(origin = 'Navigation', yaw =  90, dist = 3, speed = 0.5, depth = 0.0)
print("Task #2 done")
ahead(origin = 'Navigation', yaw = 180, dist = 3, speed = 0.5, depth = 0.0)
print("Task #3 done")
ahead(origin = 'Navigation', yaw = 270, dist = 3, speed = 0.5, depth = 0.0)
print("All done")
