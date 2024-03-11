from actions.goto import goto
from actions.spiral_movement import spiral_movement

goto(origin=(0, 0), speed=0.5, hold_time=1, radius=1)

spiral_movement(
    center=(0, 0),
    r_min=0, r_max=5,
    step=0.3,
    d_min=1, d_max=4,
    turn_max_speed=10,
    min_speed=0.2, max_speed=1.5,
    depth=1
)
