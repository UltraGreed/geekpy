#!python3
import time, sys, setproctitle, math
import numpy as np
from base import network, message, mat
from base.message import X, Y, YAW, DEPTH

# Constants.
BASE4 = 0.4
BASE3 = math.sqrt(2 * ((BASE4/2)**2))

LEFT, RIGHT, BACK, FRONT = 0, 1, 2, 3  # Phones ailases.
SIN_SAT = 0.9999                         # Sinus saturation to prevent wrong asin.

# Input parameters.
FREQ_MIN = float(sys.argv[1])  # Minimal and
FREQ_MAX = float(sys.argv[2])  # maximal frequency
OBJ      =       sys.argv[3]   # for this object.

setproctitle.setproctitle(' '.join(sys.argv))               # Set filename.py title for process.
net    = network.Net()                                      # Network communication.
robot  = network.wait_message("Coord").pos                  # Current robot position.
pinger = network.wait_message("FilteredObjects").objs[OBJ]  # Initial pinger position on seabed.

# Object offset in robot coordinates.
def offset(dist_lr, dist_bf, height, base):
    dx = dist_lr / base  # X&Y offset based
    dy = dist_bf / base  # on two projections.
    dr = math.sqrt(dx**2 + dy**2)
    dr_sat = mat.sat(dr, -SIN_SAT, SIN_SAT)
    scale = height
    if abs(dr) > 0.000001:
        scale = height * math.tan(math.asin(dr_sat)) / dr
    return [scale * dx, scale * dy]

# Send object coordinates by timer.
while net.receive():

    # Calculate Sound delays to pinger position.
    if net.id == 'SoundDelay':

        # If sound delays has come then:
        msg  = net.msg                              # read message,
        dist = msg.dist                             # distances and
        height = abs(pinger[DEPTH] - robot[DEPTH])  # calc pinger height.

        # # If frequence not in the range then exit from processing.
        # if msg.freq < FREQ_MIN or msg.freq > FREQ_MAX: 
        #     continue                                                     

        # Check which channels we have.
        channels = 4
        absent = [False, False, False, False]
        for ch in range(channels):
            if msg.freqs[ch] < FREQ_MIN or msg.freqs[ch] > FREQ_MAX:
                channels -= 1;
                absent[ch] = True

        # @todo:
        # no_front = dist[FRONT] - min(dist[LEFT],min(dist[RIGHT],dist[BACK]))
        print("Channels =", channels)

        # If channels not enough then wait next message.
        if channels < 3:
            continue

        # Calculate pinger position based on 4 channels.
        glob = mat.robot2map(robot, offset(dist[LEFT] - dist[RIGHT], dist[BACK] - dist[FRONT], height, BASE4))

        # Calculate pinger position based on 3 channels.
        if channels == 3:
            if absent[LEFT ]: glob = mat.robot2map([robot[X], robot[Y], robot[DEPTH], robot[YAW]], offset(dist[BACK] - dist[RIGHT], dist[BACK] - dist[LEFT], height, BASE3))
            if absent[RIGHT]: glob = mat.robot2map([robot[X], robot[Y], robot[DEPTH], robot[YAW]], offset(dist[BACK] - dist[RIGHT], dist[BACK] - dist[LEFT], height, BASE3))
            if absent[BACK ]: glob = mat.robot2map([robot[X], robot[Y], robot[DEPTH], robot[YAW]], offset(dist[BACK] - dist[RIGHT], dist[BACK] - dist[LEFT], height, BASE3))
            if absent[FRONT]: glob = mat.robot2map([robot[X], robot[Y], robot[DEPTH], robot[YAW]-45], offset(dist[BACK] - dist[RIGHT], dist[BACK] - dist[LEFT], height, BASE3))

        # Send message to whom it may cocern.
        net.send(message.DetectedObject(obj=OBJ, x=glob[X], y=glob[Y]))

    # Save robot position.
    elif net.id == 'Coord':  # If robot coordinates has come
        robot = net.msg.pos  # then save its position.
