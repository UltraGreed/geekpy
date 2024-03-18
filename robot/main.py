#!python3
import math
import time

import setproctitle
import sys

from base import mat, network, message
from base.message import X, Y, YAW, AXIS

########### X ##### Y # DEPTH ### YAW # PITCH ## ROLL
P = [0.50, 1.00, 0.50, 2.00, 1.50, 1.00]  # Proportional coefficients of regulator.
D = [0.00, 1.00, 0.50, 2.00, 1.50, 1.00]  # Differential coefficients of regulator.
MAX = [0.15, 0.15, 0.30, 45.00, 45.00, 45.00]  # Maximal possible velocity in stabilization mode.
MIN = [-0.15, -0.15, -0.30, -45.00, -45.00, -45.00]  # Minimal possible velocity in stabilization mode.
TIMER: float = 1 / 12  # 'Coord' message publication timer.
MIN_STAB_DIST = 0.001  # Min distance to make stabilization.


## Simple PD-regulator with saturation
def pd(dif, vel, stab_p, stab_d, sat_min, sat_max):
    val = stab_p * dif - stab_d * vel  # PD regulator.
    return mat.sat(val, sat_min, sat_max)  # Return value with saturation.


## Stabilization of XY coordinates
def pd_xy(stab, pos, vel):
    dx, dy = mat.rotate2robot(stab[X] - pos[X],  # Convert stab values
                              stab[Y] - pos[Y],  # from navigation
                              pos[YAW])  # to robot coord system.
    dist = math.sqrt(dx ** 2 + dy ** 2)  # Claculate distance to stab-point.
    if (dist < MIN_STAB_DIST):  # If distanace lees then minimal
        return  # then nothing to stab.
    min_x = MIN[X] * abs(dx) / dist  # Calculate
    min_y = MIN[Y] * abs(dy) / dist  # min and max
    max_x = MAX[X] * abs(dx) / dist  # restrictions
    max_y = MAX[Y] * abs(dy) / dist  # for axis.
    return (pd(dx, vel, P[X], D[X], min_x, max_x),
            pd(dy, vel, P[Y], D[Y], min_y, max_y))  # return PD-regulator for X and Y axis.


## Stabilization of YAW coordinate
def pd_yaw(dif, vel):
    return pd(mat.to180(dif), vel, P[YAW], D[YAW], MIN[YAW], MAX[YAW])


## Stabilization of DEPTH, PITCH and ROLL coordinates
def pd_axel(dif, vel, i):
    return pd(mat.to180(dif), vel, P[i], D[i], MIN[i], MAX[i])


coord = message.Coord()  # Sended message to all progs.
offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Position offset from current sensor data.

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=TIMER)  # Will wait messages and timer ticks.
tack = message.Tack()  # Incoming Tack message for robot control.
tack_time = 0.0  # Time of last Tack message.
tack_priority = 0  # Default tack priority.

# Wait for messages or timer
while net.receive():
    if net.id == 'Timer':
        if time.time() - tack_time > tack.time:  # If Tack command too old
            tack = message.Tack()  # then fill tack default values.
        coord.spd = [0.0] * AXIS
        for i in range(AXIS):  # In all axis:
            if mat.is_num(tack.stab[i]):  # - update stabilization values,
                if i == X or i == Y:
                    coord.spd[X], coord.spd[Y] = pd_xy(tack.stab, coord.pos, coord.vel[i])
                elif i == YAW:
                    coord.spd[YAW] = pd_yaw(tack.stab[i] - coord.pos[i], coord.vel[i])
                else:
                    coord.spd[i] = pd_axel(tack.stab[i] - coord.pos[i], coord.vel[i], i)
            if mat.is_num(tack.speed[i]):  # - and append speed values
                coord.spd[i] += tack.speed[i]  # (if 'stab' and/or 'speed' mode).
        net.send(coord)  # Send message to consumers.

    if net.id == 'Sensor':  # If sensor data has come
        msg = net.msg  # then read sensor message
        pos, vel, acc = msg.pos, msg.vel, msg.acc  # and save necessary data.
        for i in range(AXIS):  # For all axis
            if mat.is_num(pos[i]):  # correct
                coord.pos[i] = pos[i] - offset[i]  # position,
            if mat.is_num(vel[i]):  # apply
                coord.vel[i] = vel[i]  # velocity
            if mat.is_num(acc[i]):  # and
                coord.acc[i] = acc[i]  # acceleration.

    elif net.id == 'InitRobot':  # If Initialization message has come
        pos = net.msg.pos  # then save position
        for i in range(AXIS):  # and for each axel
            if mat.is_num(pos[i]):  # (if input value is number)
                offset[i] += coord.pos[i] - pos[i]  # calculate offset.

    elif net.id == 'Tack':  # If Tack message
        if net.msg.priority >= tack.priority:  # with higher priority has come
            tack = net.msg  # then save this message
            tack_time = time.time()  # and timestamp.
