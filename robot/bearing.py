#!python3
import time, sys, setproctitle, math
import numpy as np
sys.path.append('../base')
import network, message, mat
from message import X, Y, DEPTH

# Constants.
LEFT, RIGHT, BACK, FRONT = 0, 1, 2, 3  # Phones ailases.
PHONE_X = [-0.2, 0.2,  0.0, 0.0]       # Phones
PHONE_Y = [ 0.0, 0.0, -0.2, 0.2]       # coordinates.
SIN_SAT = 0.9                          # Sinus saturation to prevent wrong asin.

# Input parameters.
FREQ_MIN = float(sys.argv[1])  # Minimal and
FREQ_MAX = float(sys.argv[2])  # maximal frequency
OBJ      =       sys.argv[3]   # for this object.

setproctitle.setproctitle(' '.join(sys.argv))               # Set filename.py title for process.
net    = network.Net()                                      # Network communication.
robot  = network.wait_message("Coord").pos                  # Current robot position.
pinger = network.wait_message("FilteredObjects").objs[OBJ]  # Initial pinger position on seabed.

# First theory math, but it works asimmetrical!
# # Offset projection to one axel.
# def proj(base, diff):
#     angle = math.asin(mat.sat(diff, -base, base) / base)  # Calculated ngle and
#     return math.tan(mat.sat(angle, -TAN_SAT, TAN_SAT))    # distance of projection.
# # Object offset in robot coordinates.
# def offset(dist, height):
#     dx = height * proj(PHONE_X[RIGHT] - PHONE_X[LEFT], dist[LEFT] - dist[RIGHT])  # X&Y offset based
#     dy = height * proj(PHONE_Y[FRONT] - PHONE_Y[BACK], dist[BACK] - dist[FRONT])  # on two projections.
#     return [dx, dy]

# Offset projection to one axel.
def proj(base, diff):
    return diff / base

# Object offset in robot coordinates.
def offset(dist, height):
    dx = proj(PHONE_X[RIGHT] - PHONE_X[LEFT], dist[LEFT] - dist[RIGHT])  # X&Y offset based
    dy = proj(PHONE_Y[FRONT] - PHONE_Y[BACK], dist[BACK] - dist[FRONT])  # on two projections.
    dr = mat.sat(math.sqrt(dx**2 + dy**2), -0.9, 0.9)
    scale = height * (1.0 + 0.5 * math.tan(math.asin(dr)))
    return [scale * dx, scale * dy]

# Send object coordinates by timer.
while net.receive():

    # Calculate Sound delays to pinger position.
    if net.id() == 'SoundDelay':                                         # If sound delays has come
        msg = net.msg()                                                  # then read message.
        if msg.freq < FREQ_MIN or msg.freq > FREQ_MAX:                   # If frequence not in the range
            continue                                                     # then exit from processing.
        local = offset(msg.dist, abs(pinger[DEPTH] - robot[DEPTH]))      # Calculate pinger position in local
        glob  = mat.robot2map(robot, local)                              # and map coodrinate systems.
        net.send(message.DetectedObject(obj=OBJ, x=glob[X], y=glob[Y]))  # Send message to whom it may cocern.

    # Save robot position.
    elif net.id() == 'Coord':  # If robot coordinates has come
        robot = net.msg().pos  # then save its position.
