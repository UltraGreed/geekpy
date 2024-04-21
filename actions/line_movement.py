import time

from base import message, network
from base.message import YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25

# Coefficients for lag line following
P = 0.2
D = 0


def line_movement(speed, aruco_delay=0, timeout=None, depth=None):
    start_time = time.time()

    current_coord = network.wait_message('Coord')
    current_pos = current_coord.pos
    current_vel = current_coord.vel
    target_yaw = current_pos[YAW]
    speed_x = 0

    net = network.Net(timer=TIMER)
    while net.receive():
        if net.id == 'Timer':
            net.send(message.Tack(
                time=1.0,
                speed_y=speed,
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
                # x, y in image coordinate system
                y, x = net.msg.point

                target_yaw = current_pos[YAW] - net.msg.yaw_error

                dx_norm = x / (net.msg.image_shape[1] / 2) - 1
                speed_x = dx_norm * P - current_vel[0] * D

        elif net.id == 'DetectedObject':
            if net.msg.obj != 'Aruco' or time.time() - start_time < aruco_delay:
                continue

            return
