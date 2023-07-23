#!python3
import time, sys, setproctitle
import numpy as np
from base import network, message, mat

# Constants.
PERIOD      = 1.0                       # Publication period.
DISP_FALSE  = [ 0.5,  0.5,  0.5,  0.5]  # Dispersion of false distances.
PHONE_LEFT  = [-0.2,  0.0,  0.0]        # Coordinates of left,
PHONE_RIGHT = [ 0.2,  0.0,  0.0]        # right,
PHONE_BACK  = [ 0.0, -0.2,  0.0]        # back and
PHONE_FRONT = [ 0.0,  0.2,  0.0]        # front phones.

# Input parameters.
PINGER = [float(sys.argv[1]),  # Pinger
          float(sys.argv[2]),  # XYZ
          float(sys.argv[3])]  # coordinates.
DISP = float(sys.argv[4])      # Distance measurement dispersion.
FREQ = float(sys.argv[5])      # Signal frequency.
PROB = float(sys.argv[6])      #
DIST = float(sys.argv[7])

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=PERIOD)                # Network communication.
robot = message.Coord().pos                    # Robot position.

# Define random function for distance fluctuations.
def rnd(disp):
    return np.random.normal(0, disp)

# Distance from phone to pinger.
def dist(robot, phone):
    return mat.dist3d(mat.robot2map(robot, phone), PINGER)

# Send object coordinates by timer.
while net.receive():

    # Send data on timer if necessary.
    if net.id == 'Timer':
        is_near  = mat.dist2d(robot, PINGER) < DIST             # Is robot in the near zone?
        is_false = np.random.random()        > PROB             # Is it false solution?
        if is_near or is_false:                                 # Send message in this case.
            disp  = DISP_FALSE if is_false else DISP            # Choose disp depend on conditions.
            left  = dist(robot, PHONE_LEFT ) + rnd(disp)        # Calculate distance for left,
            right = dist(robot, PHONE_RIGHT) + rnd(disp)        # right,
            back  = dist(robot, PHONE_BACK ) + rnd(disp)        # back and
            front = dist(robot, PHONE_FRONT) + rnd(disp)        # front phones with noise.
            mini  = min(min(left, right), min(back, front))     # Calc minimal distance.
            net.send(message.SoundDelay(freq  = FREQ,           # Send message
                                        freq_left  = FREQ,      # with
                                        freq_right = FREQ,      # config
                                        freq_back  = FREQ,      # frequecy
                                        freq_front = FREQ,      # +
                                        left  = left  - mini,   # left,
                                        right = right - mini,   # right,
                                        back  = back  - mini,   # back and
                                        front = front - mini))  # front distance diffrences.

    # If robot coordinates has come then save its position.
    elif net.id == 'Coord':
        robot = net.msg.pos
