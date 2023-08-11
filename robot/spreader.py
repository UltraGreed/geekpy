import sys, os, setproctitle
import numpy as np
from base import network, message

# Linear (1) & quadric (2) thrusters' spread by axis
#######            X,      Y,   DEPTH,    YAW,  PITCH,   ROLL
SPREAD1 = [[ -300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 0: bow_left
           [  300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 1: bow_right
           [  160.00,   0.00, -300.00,   0.00,  -1.00,   1.00],  # Thruster 2: middle_left
           [ -160.00,   0.00, -300.00,   0.00,  -1.00,  -1.00],  # Thruster 3: middle_right
           [ -280.00,  67.00,    0.00,   0.43,   0.00,  -0.00],  # Thruster 4: stern_left
           [  280.00,  67.00,    0.00,  -0.43,   0.00,   0.00]]  # Thruster 5: stern_right
#######            X,      Y,   DEPTH,    YAW,  PITCH,   ROLL
SPREAD2 = [[  000.00, 000.00,  000.00, 000.00, 000.00, 000.00],  # Thruster 0: bow_left
           [  000.00, 000.00,  000.00, 000.00, 000.00, 000.00],  # Thruster 1: bow_right
           [  000.00, 000.00,  000.00, 000.00, 000.00, 000.00],  # Thruster 2: middle_left
           [  000.00, 000.00,  000.00, 000.00, 000.00, 000.00],  # Thruster 3: middle_right
           [  000.00, 000.00,  000.00, 000.00, 000.00, 000.00],  # Thruster 4: stern_left
           [  000.00, 000.00,  000.00, 000.00, 000.00, 000.00]]  # Thruster 5: stern_right

setproctitle.setproctitle(' '.join(sys.argv))  # Set process name with params.
net     = network.Net()                        # Network communication.
control = message.Control()                    # Sended Control.power data.

# Wait for incoming messages.
while net.receive():

    if net.id == 'Motion':                 # If Motion message appears then:
        speed  = net.msg.speed             # - read Motion.speed vector,
        speed1 = np.array(speed)           # - convert ot numpy array,
        speed2 = speed1 * np.abs(speed1)   # - make matrix multiplication of linear part and quadric parts.
        add    = np.matmul(SPREAD1, speed1) + np.matmul(SPREAD2, speed2)
        control.power = add.tolist()       # - save sum of parts to message,
        net.send(control)                  # - and send message to network.
