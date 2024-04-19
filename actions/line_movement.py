import time

from base import mat, message, network
from base.message import YAW

from object_recognition.object_position import get_obj_pos_bottom

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25
LINE_DEPTH = 1.16


def line_movement(speed, lag_coef=0.2, max_dist=None, timeout=None, depth=None):
    start_time = time.time()

    if not max_dist and not timeout:
        raise 'Dist or dt should be provided'

    current_pos = network.wait_message('Coord').pos
    previous_pos = current_pos
    target_yaw = current_pos[YAW]
    stab_x = 0

    net = network.Net(timer=TIMER)
    while net.receive():
        if net.id == 'Timer':
            dist = mat.dist2d(previous_pos, current_pos)
            net.send(message.Tack(
                time=1.0,
                speed_y=speed,
                stab_depth=depth,
                stab_x=stab_x,
                stab_y=current_pos[1],
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
                x, y = net.msg.point
                yaw_error = net.msg.yaw_error
                image_shape = net.msg.image_shape

                stab_x, *_ = get_obj_pos_bottom(current_pos, LINE_DEPTH, image_shape, (int(y), int(x)))

                target_yaw = current_pos[YAW] - yaw_error
                # dx_norm = y / (image_shape[1] / 2) - 1
                # speed_x = dx_norm * lag_coef
