import sys
import setproctitle

import dronecan
from dronecan import uavcan

sys.path.append('./')
from base import message, network

TIMER = 0.05
_PORT_NAME = 'vcan0'


def send_raw_command(node, power):
    message = uavcan.equipment.esc.RawCommand(cmd=power.power)
    node.broadcast(message)


def main():
    net = network.Net(timer=TIMER)
    power = message.Control()

    node = dronecan.make_node(_PORT_NAME, node_id=100, bitrate=500000)

    while net.receive():

        if net.id() == "Control":
            power.power = net.msg().power
            send_raw_command(node, power)

    node.close()


if __name__ == '__main__':
    main()
