#!python3
# @todo: Improve pd_xy() to ellipse projections.
import math
import setproctitle
import sys
import time

from base import mat, network, message
from base.message import X, Y, YAW, AXIS

########### X ##### Y # DEPTH ### YAW # PITCH ## ROLL
P   = [100.00, 100.00,   1.00,   3.00, 000.00, 000.00]  # Proportional coefficients of regulator.
D   = [  1.00,   1.00,   1.00,   3.00, 000.00, 000.00]  # Differential coefficients of regulator.
MAX = [  0.70,   0.70,   1.00,  60.00, 000.00, 000.00]  # Maximal possible velocity in stabilization mode.
MIN = [ -0.70,  -0.70,  -1.00, -60.00, 000.00, 000.00]  # Minimal possible velocity in stabilization mode.
TIMER = 0.05                                            # 'Motion' message publication timer.
MIN_STAB_DIST = 0.001                                   # Min distance to make stabilization.


## Simple PD-regulator with saturation
def pd(dif, vel, stab_p, stab_d, sat_min, sat_max):
    val = stab_p * dif - stab_d * vel  # PD regulator.
    return mat.sat(val, sat_min, sat_max)  # Return value with saturation.


## Stabilization of XY coordinates
def pd_xy(speed, stab, pos, vel):
    sx = stab[X] if mat.is_num(stab[X]) else pos[X]                # Save stabilization
    sy = stab[Y] if mat.is_num(stab[Y]) else pos[Y]                # values X and/or Y (if exists).
    dx, dy = mat.rotate2robot(sx - pos[X], sy - pos[Y], pos[YAW])  # Convert stab values to robot coords.
    dist = math.sqrt(sx * sx + sy * sy)                            # Claculate distance to stab-point.
    if (dist < MIN_STAB_DIST): return                              # If distanace lees then minimal then nothing to stab.
    min_x = MIN[X] * abs(dx) / dist                                # Calculate
    min_y = MIN[Y] * abs(dy) / dist                                # min and max
    max_x = MAX[X] * abs(dx) / dist                                # restrictions
    max_y = MAX[Y] * abs(dy) / dist                                # for axis.
    speed[X] = pd(dx, vel, P[X], D[X], min_x, max_x)               # Apply PD-regulator for X
    speed[Y] = pd(dy, vel, P[Y], D[Y], min_y, max_y)               # and Y axis.


## Stabilization of YAW coordinate
def pd_yaw(speed, dif, vel):
    speed[YAW] = pd(mat.to180(dif), vel, P[YAW], D[YAW], MIN[YAW], MAX[YAW])


## Stabilization of DEPTH, PITCH and ROLL coordinates
def pd_axel(speed, dif, vel, i):
    speed[i] = pd(mat.to180(dif), vel, P[i], D[i], MIN[i], MAX[i])


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=TIMER)                 # Will wait messages and timer ticks.
tack = message.Tack()                          # Incoming Tack message for robot control.
tack_time = 0.0                                # Time of last Tack message.
pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]           # Incoming position
vel = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]           # and velocity data.

while net.receive():  # Waiting for timer ticks and messages.

    if net.id == 'Timer':                         # On timer event:
        if time.time() - tack_time > tack.time:   # If Tack command too old
            tack = message.Tack()                 # then fill tack default values.
        motion = message.Motion()                 # Create Motion message.
        for i in range(AXIS):                     # In all axis:
            if mat.is_num(tack.stab[i]):          # - update stabilization values,
                if i == X or i == Y: pd_xy(motion.speed, tack.stab, pos, vel[i])
                elif i == YAW:      pd_yaw(motion.speed, tack.stab[i] - pos[i], vel[i])
                else:              pd_axel(motion.speed, tack.stab[i] - pos[i], vel[i], i)
            if mat.is_num(tack.speed[i]):         # - and append speed values
                motion.speed[i] += tack.speed[i]  # (if 'stab' and/or 'speed' mode).
        net.send(motion)

    elif net.id == 'Tack':       # If Tack message has come
        tack = net.msg           # then save this message
        tack_time = time.time()  # and its timestamp.

    elif net.id == 'Coord':          # Save position
        msg = net.msg                # and velocity
        pos, vel = msg.pos, msg.vel  # from incoming message.
