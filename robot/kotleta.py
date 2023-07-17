import sys
import setproctitle

import dronecan
from dronecan import uavcan

from base import message, network

_PORT_NAME = 'can0'
_MAX_POWER = 7000


def send_raw_command(node, power):
    cmd = [ 0, 0, 0, 0, 0, 0]
    rotation_params = [ 1, 1, -1, 1, -1, 1 ]

    for i in range(len(cmd)):
        current_power = round(power.power[i] / 100 * _MAX_POWER)
        cmd[i] = current_power * rotation_params[i]

    message = uavcan.equipment.esc.RawCommand(cmd=cmd)
    node.broadcast(message)


def main():
    setproctitle.setproctitle(' '.join(sys.argv)) 

    net = network.Net()
    power = message.Control()

    node = dronecan.make_node(_PORT_NAME, node_id=100, bitrate=500000)

    while net.receive():

        if net.id == "Control":
            power.power = net.msg.power
            send_raw_command(node, power)

    node.close()


if __name__ == '__main__':
    main()
