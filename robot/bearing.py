#!python3
import time, sys, setproctitle, math
import numpy as np
from base import network, message, mat
from base.message import X, Y, DEPTH

# Constants.
LEFT, RIGHT, BACK, FRONT = 0, 1, 2, 3  # Phones ailases.
PHONE_X = [-0.2, 0.2,  0.0, 0.0]       # Phones
PHONE_Y = [ 0.0, 0.0, -0.2, 0.2]       # coordinates.
SIN_SAT = 0.99                         # Sinus saturation to prevent wrong asin.

# Input parameters.
FREQ_MIN = float(sys.argv[1])  # Minimal and
FREQ_MAX = float(sys.argv[2])  # maximal frequency
OBJ      =       sys.argv[3]   # for this object.

setproctitle.setproctitle(' '.join(sys.argv))               # Set filename.py title for process.
net    = network.Net()                                      # Network communication.
robot  = network.wait_message("Coord").pos                  # Current robot position.
pinger = network.wait_message("FilteredObjects").objs[OBJ]  # Initial pinger position on seabed.

# Object offset in robot coordinates.
def offset(dist, height):
    dx = (dist[LEFT] - dist[RIGHT]) / (PHONE_X[RIGHT] - PHONE_X[LEFT])  # X&Y offset based
    dy = (dist[BACK] - dist[FRONT]) / (PHONE_Y[FRONT] - PHONE_Y[BACK])  # on two projections.
    dr = math.sqrt(dx**2 + dy**2)
    dr_sat = mat.sat(dr, -SIN_SAT, SIN_SAT)
    scale = (height * math.tan(math.asin(dr_sat)) / dr) if abs(dr) > 0.000001 else height
    return [scale * dx, scale * dy]

# Send object coordinates by timer.
while net.receive():

    # Calculate Sound delays to pinger position.
    if net.id == 'SoundDelay':                                           # If sound delays has come
        msg = net.msg                                                    # then read message.
        if msg.freq < FREQ_MIN or msg.freq > FREQ_MAX:                   # If frequence not in the range
            continue                                                     # then exit from processing.
        local = offset(msg.dist, abs(pinger[DEPTH] - robot[DEPTH]))      # Calculate pinger position in local
        glob  = mat.robot2map(robot, local)                              # and map coodrinate systems.
        net.send(message.DetectedObject(obj=OBJ, x=glob[X], y=glob[Y]))  # Send message to whom it may cocern.

    # Save robot position.
    elif net.id == 'Coord':  # If robot coordinates has come
        robot = net.msg.pos  # then save its position.
