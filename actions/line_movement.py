import time

from base import message, network, mat
from base.message import YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25

# Coefficients for lag line following
P = 0.8
D = 0
MAX_X_SPEED = 0.2


def line_movement(speed: float,
                  object_delay: float,
                  exit_object: str,
                  exit_delay: float,
                  timeout: float = None,
                  depth: float = None):
    start_time = time.time()

    current_coord = network.wait_message('Coord')
    current_pos = current_coord.pos
    current_vel = current_coord.vel

    target_yaw = current_pos[YAW]
    speed_x = 0

    was_object_detected = False
    object_detected_time = 0

    net = network.Net(timer=TIMER)
    while net.receive():
        if net.id == 'Timer':
            if was_object_detected and time.time() - object_detected_time > exit_delay:
                return  # Action ends here

            yaw_diff = abs(target_yaw - current_pos[YAW])
            speed_coef = 1 - mat.sat(yaw_diff / 45, 0, 1)

            net.send(message.Tack(
                time=1.0,
                speed_y=speed * speed_coef,
                speed_x=speed_x,
                stab_depth=depth,
                stab_yaw=target_yaw,
                stab_pitch=0.0,
                stab_roll=0.0
            ))

            if timeout is not None and time.time() - start_time > timeout:
                return

        elif net.id == 'Coord':
            # Update robot position and velocity
            current_pos = net.msg.pos
            current_vel = net.msg.vel

        elif net.id == 'Line':
            if net.msg.is_detected:
                target_yaw = current_pos[YAW] - net.msg.yaw_error

                speed_x = min(abs(net.msg.lag_error * P - current_vel[0] * D), MAX_X_SPEED)
                speed_x *= -1 if net.msg.lag_error < 0 else 1

        elif net.id == 'DetectedObject':
            if (net.msg.obj != exit_object
                    or time.time() - start_time < object_delay
                    or was_object_detected):
                continue

            object_detected_time = time.time()
            was_object_detected = True
