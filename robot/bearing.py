#!python3
# @todo: 
import time, sys, setproctitle, math
import numpy as np
from base import network, message, mat
from base.message import X, Y, YAW, DEPTH

# Constants.
BASE       = 0.4                       # 4 phones base (cross dist).
DIST_TRASH = 1.5 * BASE                # Distance trashold to drop wrong distance defference.
SIN_SAT    = 0.99                      # Sinus saturation to prevent wrong asin.
LEFT, RIGHT, BACK, FRONT = 0, 1, 2, 3  # Phones ailases.

# Input parameters.
FREQ_MIN = float(sys.argv[1])  # Minimal and
FREQ_MAX = float(sys.argv[2])  # maximal frequency
OBJ      =       sys.argv[3]   # for this object.

setproctitle.setproctitle(' '.join(sys.argv))               # Set filename.py title for process.
net    = network.Net()                                      # Network communication.
robot  = network.wait_message("Coord").pos                  # Current robot position.
pinger = network.wait_message("FilteredObjects").objs[OBJ]  # Initial pinger position on seabed.

# Object offset in robot coordinates.
def offset(left, right, back, front, height):
    dx = (left - right) / BASE  # X&Y offset based
    dy = (back - front) / BASE  # on two projections.
    dr = math.sqrt(dx**2 + dy**2)
    dr_sat = mat.sat(dr, -SIN_SAT, SIN_SAT)
    scale = height
    if abs(dr) > 0.000001:
        scale = height * math.tan(math.asin(dr_sat)) / dr
    return [scale * dx, scale * dy]

# Return false if dist[channel] out of range in comparison with other channels.
def out_of_range(dist, channel):
    mn =  100000000
    mx = -100000000
    for ch in range(len(dist)):
        if ch != channel:
            mn = min(mn, dist[ch])
            mx = max(mx, dist[ch])
    if max(dist[channel] - mx, mn - dist[channel]) > DIST_TRASH:
        return True
    return False


# Send object coordinates by timer.
while net.receive():

    # Calculate Sound delays to pinger position.
    if net.id == 'SoundDelay':

        # If sound delays has come then:
        msg    = net.msg                            # Read message,
        dist   = msg.dist                           # distances,
        freqs  = msg.freqs                          # frequencies and
        height = abs(pinger[DEPTH] - robot[DEPTH])  # calc pinger height.

        # Check cool channels basing on frequency.
        channels = 4
        for ch in range(channels):
            if freqs[ch] < FREQ_MIN or freqs[ch] > FREQ_MAX or out_of_range(dist, ch):
                dist[ch] = -1
            if dist[ch] < 0:
                channels -= 1

        # If channels not enough then wait next message.
        if channels < 3:
            continue

        # Make virtual distance if it possible.
        if dist[LEFT ] < 0: dist[LEFT ] = dist[BACK ] + dist[FRONT] - dist[RIGHT]
        if dist[RIGHT] < 0: dist[RIGHT] = dist[BACK ] + dist[FRONT] - dist[LEFT ]
        if dist[BACK ] < 0: dist[BACK ] = dist[LEFT ] + dist[RIGHT] - dist[FRONT]
        if dist[FRONT] < 0: dist[FRONT] = dist[LEFT ] + dist[RIGHT] - dist[BACK ]

        # Send message to whom it may cocern.
        local = offset(dist[LEFT], dist[RIGHT], dist[BACK], dist[FRONT], height)
        glob  = mat.robot2map(robot, local)
        net.send(message.DetectedObject(obj=OBJ, x=glob[X], y=glob[Y]))

    # Save robot position.
    elif net.id == 'Coord':  # If robot coordinates has come
        robot = net.msg.pos  # then save its position.
