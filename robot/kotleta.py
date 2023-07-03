import sys
import setproctitle
import threading

import dronecan
from dronecan import uavcan

sys.path.append('./')
from base import message, network

TIMER = 0.05
_PORT_NAME = 'vcan0'
_COMMAND_TIMEOUT = 5
_COMMANDS_PER_SECOND = 10000


def handle_recieve(net: network.Net, 
                   power: message.Control, 
                   timeout_event: threading.Event,
                   close_event: threading.Event):
    while net.receive():

        if close_event.is_set():
            break;

        if net.id() == "Control":
            power.power = net.msg().power
            timeout_event.set()


def send_raw_command(node, power):
    message = uavcan.equipment.esc.RawCommand(cmd=power.power)
    node.broadcast(message)


def main():
# setproctitle.setproctitle(sys.argv[0])

    net = network.Net(timer=TIMER)
    power = message.Control()
    timeout_event = threading.Event()
    close_event = threading.Event()

    node = dronecan.make_node(_PORT_NAME, node_id=123, bitrate=100)

    recieve_thread = threading.Thread(target=handle_recieve, 
                                      args=(net, power, timeout_event, close_event))
    recieve_thread.start()

    def timeout_call():
        power.power = [0, 0, 0, 0, 0, 0]
    
    timeout_handle = node.defer(_COMMAND_TIMEOUT, timeout_call)
    timeout_handle.remove()

    while True:
        try:
            node.spin(1 / _COMMANDS_PER_SECOND)
            send_raw_command(node, power)

            if timeout_event.is_set():
                timeout_event.clear()
                timeout_handle.try_remove()
                timeout_handle = node.defer(_COMMAND_TIMEOUT, timeout_call)

        except KeyboardInterrupt:
            break
    
    close_event.set()

    recieve_thread.join()

    node.close()


if __name__ == '__main__':
    main()
