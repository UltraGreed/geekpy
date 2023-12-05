import sys
import setproctitle
import math

import dronecan
from dronecan import uavcan

import numpy as np

from base import message, network

c0_to_c1 = { 2: 0, }

_MAX_POWER = 7000
_NO_SENSE = 0.0285

# Linear (1) & quadric (2) thrusters' spread by axis
#######            X,      Y,   DEPTH,    YAW,  PITCH,   ROLL
SPREAD1 = [[ -300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 0: bow_left
           [  300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 1: bow_right
           [  160.00,   0.00, -300.00,   0.00,  -1.00,   1.00],  # Thruster 2: middle_left
           [ -160.00,   0.00, -300.00,   0.00,  -1.00,  -1.00],  # Thruster 3: middle_right
           [ -280.00,  67.00,    0.00,   0.43,   0.00,  -0.00],  # Thruster 4: stern_left
           [  280.00,  67.00,    0.00,  -0.43,   0.00,   0.00]]  # Thruster 5: stern_right


def send_raw_command(node_main, node_spare, power):
    cmd = [ 0, 0, 0, 0, 0, 0]
    rotation_params = [ 1, -1, -1, 1, -1, 1 ]

    for i in range(len(cmd)):
        sign = int(math.copysign(1, power.power[i]))
        current_power = round(abs(power.power[i]) / 100 * _MAX_POWER)

        if current_power > 8191:
            current_power = 8191 

        cmd[i] = current_power * rotation_params[i] * sign

        if abs(cmd[i]) < _NO_SENSE * _MAX_POWER:
            cmd[i] = 0

    cmd_spare = [ 0, 0, 0, 0, 0, 0]
    for key, value in c0_to_c1.items():
        cmd_spare[value] = cmd[key] 

    node_main.broadcast(uavcan.equipment.esc.RawCommand(cmd=cmd))
    node_spare.broadcast(uavcan.equipment.esc.RawCommand(cmd=cmd_spare))


def matrixing(speed):
    return (np.array(SPREAD1) @ np.array(speed)).tolist()


def main():
    setproctitle.setproctitle(' '.join(sys.argv)) 

    net = network.Net()
    power = message.Control()

    node_can0 = dronecan.make_node("can0", node_id=100, bitrate=500000)
    node_can1 = dronecan.make_node("can1", node_id=101, bitrate=500000)

    # node.add_handler(uavcan.equipment.esc.Status, lambda msg: print(dronecan.to_yaml(msg)))

    # try:
    #     node.spin()
    # except KeyboardInterrupt:
    #     return

    while net.receive():

        if net.id == "Control":
            power.power = net.msg.power
            send_raw_command(node_can0, node_can1, power)
            continue

        if net.id == "Coord":
            power.power = matrixing(net.msg.speed)
            send_raw_command(node_can0, node_can1, power)

    node_can0.close()
    node_can1.close()


if __name__ == '__main__':
    main()
