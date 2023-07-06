#!python3
import time, sys, setproctitle
import numpy as np
sys.path.append('../base')
import network, message, mat

# Constants.
LEFT       = [-0.2,  0.0,  0.0]  # Coordinates of left,
RIGHT      = [ 0.2,  0.0,  0.0]  # right,
BACK       = [ 0.0, -0.2,  0.0]  # back and
FRONT      = [ 0.0, -0.2,  0.0]  # front phones.

# Input parameters.
FREQ_MIN = float(sys.argv[1])
FREQ_MAX = float(sys.argv[2])
OBJ      = float(sys.argv[3])
DEPTH    = float(sys.argv[4])

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=PERIOD)  # Network communication.
pos = message.Coord().pos        # Robot position.

# Define random function for distance fluctuations.
def rnd(disp):
    return np.random.normal(0, disp)

# Send object coordinates by timer.
while net.receive():

    if net.id() == 'Timer':                                                 # Send data on timer if necessary.
        is_near  = mat.dist2d(pos, OBJ) < DIST                              # Is robot in the near zone?
        is_false = np.random.random()   > PROB                              # Is it false solution?
        if is_near or is_false:                                             # Send message in this case.
            disp  = DISP_FALSE if is_false else DISP                        # Chose disp depend on conditions.
            left  = mat.dist3d(mat.robot2map(pos, LEFT ), OBJ) + rnd(disp)  # Calculate distance for left,
            right = mat.dist3d(mat.robot2map(pos, RIGHT), OBJ) + rnd(disp)  # right,
            back  = mat.dist3d(mat.robot2map(pos, BACK ), OBJ) + rnd(disp)  # back and
            front = mat.dist3d(mat.robot2map(pos, FRONT), OBJ) + rnd(disp)  # front phones with noise.
            mini  = min(min(left, right), min(back, front))                 # Calc minimal distance.
            net.send(message.SoundDelay(                                    # Send message
                freq  = FREQ,                                               # with config frequecy and
                left  = left  - mini,                                       # left,
                right = right - mini,                                       # right,
                back  = back  - mini,                                       # back and
                front = front - mini))                                      # front distance diffrences.

    elif net.id() == 'Coord':  # If robot coordinates has come
        pos = net.msg().pos    # then save its position.
