from actions.line_movement import line_movement
from actions import photosave
from actions.init_robot import init_robot
from actions.target_homing import target_homing
from actions.tack import tack
from actions.stab import stab


mission_depth = 0.5
pool_depth = 1.15

lower_depth = 1.0
upper_depth = 0.5
target_depth = lower_depth

line_speed = 0.2
homing_speed = 0.1

obj_order = [
    ("SquareYellow", lower_depth),
    ("TriangleGreen", upper_depth),
    ("SquareYellow", lower_depth),
    ("TriangleGreen", upper_depth),
    ("SquareYellow", lower_depth),
]

init_robot(yaw=0, depth=0, x=0, y=0)

photosave.start("Bottom", None)
photosave.start("Front", None)

print("circle red")
stab(origin="CircleRed", yaw=0.0, depth=lower_depth, dt=3)

print("green")
line_movement(exit_object=obj_order[0][0], depth=obj_order[0][1], speed=line_speed, timeout=10, object_delay=0, exit_delay=1)
print("yellow")
line_movement(exit_object=obj_order[1][0], depth=obj_order[1][1], speed=line_speed, timeout=10, object_delay=0, exit_delay=1)
print("green")
line_movement(exit_object=obj_order[2][0], depth=obj_order[2][1], speed=line_speed, timeout=10, object_delay=0, exit_delay=1)
print("yellow")
line_movement(exit_object=obj_order[3][0], depth=obj_order[3][1], speed=line_speed, timeout=10, object_delay=0, exit_delay=1)
print("green")
line_movement(exit_object=obj_order[4][0], depth=obj_order[4][1], speed=line_speed, timeout=10, object_delay=0, exit_delay=1)

print("target")
target_homing(depth=target_depth, speed=homing_speed)

photosave.stop("Bottom")
photosave.stop("Front")
