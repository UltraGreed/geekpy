#!python3
import time, sys, setproctitle, random, math
import numpy as np
sys.path.append('../base')
import mat, network, message
from message import X, Y

# Input parameters.
REAL_X = float(sys.argv[1])
REAL_Y = float(sys.argv[2])
OBJ    =       sys.argv[3]
DISP   = float(sys.argv[4])
PERIOD = float(sys.argv[5])
PROB   = float(sys.argv[6])
DIST   = float(sys.argv[7])

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=PERIOD)                # Network communication.
pos = message.Coord().pos                      # Robot position.

# Send object coordinates by timer.
while net.receive():

    if net.id() == 'Timer':
        x = np.random.normal(0, DISP)
        y = np.random.normal(0, DISP)
        prob = random.random()
        if mat.dist2d(pos, [REAL_X, REAL_Y]) < DIST:
            if prob <= PROB:
                x += REAL_X
                y += REAL_Y
            else:
                x += pos[X]
                y += pos[Y]
            net.send(message.DetectedObject(obj=OBJ, x=x, y=y))
        elif prob > PROB:
            x += pos[X]
            y += pos[Y]
            net.send(message.DetectedObject(obj=OBJ, x=x, y=y))

    elif net.id() == 'Coord':
        pos = net.msg().pos
