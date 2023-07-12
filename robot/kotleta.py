import sys
import setproctitle

import dronecan
from dronecan import uavcan

sys.path.append('./')
from base import message, network

_PORT_NAME = 'can0'

_MIN_POWER = 400
_MAX_POWER = 4000


def send_raw_command(node, power):
    cmd = [ 0, 0, 0, 0, 0, 0]
    rotation_params = [ 1, 1, -1, 1, -1, 1 ]

    for i in range(6):
        current_power = round(power.power[i] / 100 * (_MAX_POWER - _MIN_POWER))

        if current_power > 0:
            current_power += _MIN_POWER
        elif current_power < 0:
            current_power -= _MIN_POWER

        cmd[i] = current_power * rotation_params[i]

    message = uavcan.equipment.esc.RawCommand(cmd=cmd)
    node.broadcast(message)


def main():
    setproctitle.setproctitle(' '.join(sys.argv)) 

    net = network.Net()
    power = message.Control()

    node = dronecan.make_node(_PORT_NAME, node_id=100, bitrate=500000)

    node.add_handler(dronecan.uavcan.equipment.esc.Status, lambda msg: print(dronecan.to_yaml(msg)))

    while net.receive():

        if net.id == "Control":
            power.power = net.msg.power
            send_raw_command(node, power)

    node.close()


if __name__ == '__main__':
    main()
