from actions.goto import goto
from actions.spiral_movement import spiral_movement


goto(origin=(-10, -5), speed=0.5, hold_time=1)
spiral_movement(center=(-10, -5), step=0.5, turn_n=10, spiral_speed=0.3, depth=1)
