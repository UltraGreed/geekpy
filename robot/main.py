#!python3
import math
import time

import setproctitle
import sys

from base import mat, network, message
from base.message import X, Y, DEPTH, YAW, PITCH, ROLL, AXIS

######### X #### Y # DEPTH ## YAW ### PITCH # ROLL
P =   [ 0.50,  2.00,  0.50,   2.00,   1.50,   1.00]  # Proportional coefficients of regulator.
D =   [ 0.00,  0.00,  0.50,   2.00,   1.50,   1.00]  # Differential coefficients of regulator.
MAX = [ 0.15,  0.15,  0.30,  45.00,  45.00,  45.00]  # Maximal possible velocity in stabilization mode.
MIN = [-0.15, -0.15, -0.30, -45.00, -45.00, -45.00]  # Minimal possible velocity in stabilization mode.
TIMER: float = 1 / 12  # 'Coord' message publication timer.
MIN_STAB_DIST = 0.001  # Min distance to make stabilization.


# Simple PD-regulator with saturation
def pd(error, velocity, i):
    speed = P[i] * error - D[i] * velocity
    return mat.sat(speed, MIN[i], MAX[i])  # Return value with saturation.


# Stabilization of XY coordinates
def pd_xy(absolute_xy, robot_pos, velocity):
    # Convert stabilization xy from absolute to relative coordinates
    dx, dy = mat.rotate2robot(
        absolute_xy[X] - robot_pos[X],
        absolute_xy[Y] - robot_pos[Y],
        robot_pos[YAW]
    )

    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance < MIN_STAB_DIST:
        return 0, 0

    min_x = MIN[X] * abs(dx) / distance
    max_x = MAX[X] * abs(dx) / distance
    speed_x = P[X] * dx - D[X] * velocity

    min_y = MIN[Y] * abs(dy) / distance
    max_y = MAX[Y] * abs(dy) / distance
    speed_y = P[Y] * dy - D[Y] * velocity

    return (mat.sat(speed_x, min_x, max_x),
            mat.sat(speed_y, min_y, max_y))


def main():
    coord = message.Coord()
    offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Position offset from current sensor data.

    tack = message.Tack()
    tack_time = 0.0  # Time of last Tack message.
    tack.priority = 0  # Default tack priority.

    net = network.Net(timer=TIMER)  # Will wait messages and timer ticks.
    while net.receive():
        if net.id == 'Timer':
            if time.time() - tack_time > tack.time:  # If Tack command is outdated,
                tack = message.Tack()  # reset it

            coord.spd = [0.0] * AXIS

            # Calculation of stabilization
            for i in [DEPTH, YAW, PITCH, ROLL]:
                if tack.stab[i] is not None:
                    coord.spd[i] = pd(mat.to180(tack.stab[i] - coord.pos[i]), coord.vel[i], i)

            # XY stabilization is a bit unique
            if tack.stab[X] is not None and tack.stab[Y] is not None:
                coord.spd[X], coord.spd[Y] = pd_xy(tack.stab, coord.pos, coord.vel[i])

            # Supplementation of raw speed values
            for i in range(AXIS):
                if tack.speed[i]:
                    coord.spd[i] += tack.speed[i]

            net.send(coord)  # Send message to consumers.

        if net.id == 'Sensor':
            # Update position, velocity and acceleration from sensors
            for i in range(AXIS):
                if net.msg.pos[i] is not None:
                    coord.pos[i] = net.msg.pos[i] - offset[i]
                if net.msg.vel[i] is not None:
                    coord.vel[i] = net.msg.vel[i]
                if net.msg.acc[i] is not None:
                    coord.acc[i] = net.msg.acc[i]

        elif net.id == 'InitRobot':
            # Set all coordinates to given ones
            for i in range(AXIS):
                if net.msg.pos[i] is not None:
                    offset[i] += coord.pos[i] - net.msg.pos[i]

        elif net.id == 'Tack':
            # Replace tack with newer one
            if net.msg.priority >= tack.priority:
                tack = net.msg
                tack_time = time.time()


if __name__ == '__main__':
    setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
    main()
