#!python3 regulator.py
# @todo: Improve stab_xy() to ellipse projections.
import time, sys
sys.path.append('../base')
import mat, network, message
from message import X, Y, YAW, AXIS

############### X ##### Y # DEPTH ### YAW # PITCH ## ROLL
STAB_P  = [  0.50,   0.50, 000.00,   5.00, 000.00, 000.00]  # Proportional coefficients of regulator
STAB_D  = [  0.50,   0.50, 000.00,   5.00, 000.00, 000.00]  # Differential coefficients of regulator
SAT_MAX = [  0.70,   0.70, 000.00,  30.00, 000.00, 000.00]  # Maximal possible velocity in stabilization mode
SAT_MIN = [ -0.70,  -0.70, 000.00, -30.00, 000.00, 000.00]  # Minimal possible velocity in stabilization mode
TIMER   = 0.05  # 'Motion' message publication timer

## Stabilization of common coordinates like DEPTH, PITCH and ROLL
def stab_coord(speed, dif, vel, i):
    val      = STAB_P[i] * dif - STAB_D[i] * vel     # PD regulator.
    speed[i] = mat.sat(val, SAT_MIN[i], SAT_MAX[i])  # Return value to axel.

## Stabilization of XY coordinates
def stab_xy(speed, stab, pos, vel):
    sx = stab[X] if mat.is_num(stab[X]) else pos[X]             # Save stabilization
    sy = stab[Y] if mat.is_num(stab[Y]) else pos[Y]             # values X and/or Y (if exists).
    dx, dy = mat.map2robot(sx - pos[X], sy - pos[Y], pos[YAW])  # Convert stab values to robot coords.
    stab_coord(speed, dx, vel, X)                               # Apply 
    stab_coord(speed, dy, vel, Y)                               # 

## Stabilization of YAW coordinate
def stab_yaw(speed, dif, vel):
    stab_coord(speed, mat.to180(dif), vel, YAW)

net       = network.Net(timer=TIMER)        # Will wait messages and timer ticks.
tack      = message.Tack()                  # Incoming Tack message for robot control.
tack_time = 0.0                             # Time of last Tack message.
pos       = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Incoming position
vel       = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # and velocity data.

while net.receive():  # Waiting for timer ticks and messages.

    if net.id() == 'Timer':                       # On timer event:
        if time.time() - tack_time > tack.time:   # If Tack command too old
            tack = message.Tack()                 # then fill tack default values.
        motion = message.Motion()                 # Create Motion message.
        for i in range(AXIS):                     # In all axis:
            if mat.is_num(tack.stab[i]):          # - update stabilization values,
                if i == X or i == Y:
                    stab_xy(motion.speed, tack.stab, pos, vel[i])
                elif i == YAW:
                    stab_yaw(motion.speed, tack.stab[i] - pos[i], vel[i])
                else:
                    stab_coord(motion.speed, tack.stab[i] - pos[i], vel[i], i)
            if mat.is_num(tack.speed[i]):         # - and append speed values
                motion.speed[i] += tack.speed[i]  # (if 'stab' and/or 'speed' mode).
        net.send(motion)

    elif net.id() == 'Tack':     # If Tack message has come
        tack      = net.msg()    # then save this message
        tack_time = time.time()  # and its timestamp.

    elif net.id() == 'Coord':        # Save position
        msg = net.msg()              # and velocity
        pos, vel = msg.pos, msg.vel  # from incoming message.
