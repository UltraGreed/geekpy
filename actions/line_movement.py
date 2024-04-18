import math
import time

from base import mat, message, network
from base.message import YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25


def line_movement(speed, lag_coef=0.2, max_dist=None, timeout=None, depth=None):
    start_time = time.time()

    if not max_dist and not timeout:
        raise 'Dist or dt should be provided'

    current_pos = network.wait_message('Coord').pos
    previous_pos = current_pos
    target_yaw = current_pos[YAW]
    speed_x = 0

    net = network.Net(timer=TIMER)
    while net.receive():
        if net.id == 'Timer':
            dist = mat.dist2d(previous_pos, current_pos)
            net.send(message.Tack(
                time=1.0,
                speed_x=speed_x,
                speed_y=speed,
                stab_depth=depth,
                stab_yaw=target_yaw,
                stab_pitch=0.0,
                stab_roll=0.0
            ))

            if timeout is not None and time.time() - start_time > timeout:
                return

            if max_dist is not None and dist > max_dist:
                return

        elif net.id == 'Coord':  # If coordinates has come
            current_pos = net.msg.pos  # then save robot position.

        elif net.id == 'Line':
            if net.msg.is_detected:
                a, b = net.msg.coefs
                b_norm = b * 2 / net.msg.image_shape[1]
                b_norm = min(abs(b_norm), 1) * b_norm / abs(b_norm)
                yaw_error = math.degrees(math.atan(a))
                target_yaw = current_pos[YAW] - yaw_error
                speed_x = float(b_norm) * lag_coef
