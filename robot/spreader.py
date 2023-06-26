import sys

import numpy as np

sys.path.append('./')
from base import network, message

# Linear (1) & quadric (2) thrusters' spread by axis
#######     X       Y       DEPTH   YAW     PITCH   ROLL
SPREAD1 = [[000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 0: bow_left
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 1: bow_right
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 2: middle_left
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 3: middle_right
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 4: stern_left
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00]]  # Thruster 5: stern_right
#######     X       Y       DEPTH   YAW     PITCH   ROLL
SPREAD2 = [[000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 0: bow_left
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 1: bow_right
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 2: middle_left
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 3: middle_right
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00],  # Thruster 4: stern_left
           [000.00, 000.00, 000.00, 000.00, 000.00, 000.00]]  # Thruster 5: stern_right

net     = network.Net()      # Network communication.
control = message.Control()  # Sended Control.power data.

while net.receive():  # Wait for incoming messages.

    if net.id() == 'Motion':                 # If Motion message appears then:
        speed  = net.msg().speed             # - read Motion.speed vector,
        speed1 = np.array(speed)             # - convert ot numpy array,
        speed2 = speed1 * np.abs(speed1)     # - make signed speed^2 of each value,
        add    = np.matmul(SPREAD1, speed1)  # - make matrix multiplication of linear part,
               + np.matmul(SPREAD2, speed2)  # - make matrix multiplication of quadric part,
        control.power = add.to_list()        # - save sum of parts to message,
        net.send(control)                    # - and send message to network.
