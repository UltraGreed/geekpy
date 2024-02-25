import sys
import setproctitle
import math
import random

import dronecan
from dronecan import uavcan

import numpy as np

from base import message, network

_MAX_POWER = 7000
_MIN_POWER = 200

# Linear (1) & quadric (2) thrusters' spread by axis
#######            X,      Y,   DEPTH,    YAW,  PITCH,   ROLL
SPREAD1 = [[ -300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 0: bow_left
           [  300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 1: bow_right
           [  160.00,   0.00, -300.00,   0.00,  -1.00,   1.00],  # Thruster 2: middle_left
           [ -160.00,   0.00, -300.00,   0.00,  -1.00,  -1.00],  # Thruster 3: middle_right
           [ -280.00,  67.00,    0.00,   0.43,   0.00,  -0.00],  # Thruster 4: stern_left
           [  280.00,  67.00,    0.00,  -0.43,   0.00,   0.00]]  # Thruster 5: stern_right


def send_raw_command(node, power):
    cmd = [ 0, 0, 0, 0, 0, 0]
    rotation_params = [ 1, -1, -1, 1, -1, 1 ]

    for i in range(len(cmd)):
        sign = int(math.copysign(1, power[i]))
        current_power = round(abs(power[i]) / 100 * _MAX_POWER)

        if current_power > 8191:
            current_power = 8191 

        cmd[i] = current_power * rotation_params[i] * sign

        if abs(cmd[i]) < _MIN_POWER and power / (_MIN_POWER / _MAX_POWER) < random.random():
            cmd[i] = 0

    node.broadcast(uavcan.equipment.esc.RawCommand(cmd=cmd))


def matrixing(speed):
    return (np.array(SPREAD1) @ np.array(speed)).tolist()


def main():
    setproctitle.setproctitle(' '.join(sys.argv)) 

    net = network.Net()
    power = message.Control()

    node = dronecan.make_node("can0", node_id=100, bitrate=500000)

    while net.receive():

        if net.id == "Control":
            power.power = net.msg.power
            send_raw_command(node, power.power)

        if net.id == "Coord":
            power.power = matrixing(net.msg.speed)
            send_raw_command(node, power.power)

    node.close()


if __name__ == '__main__':
    main()
