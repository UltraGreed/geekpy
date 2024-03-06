import sys
import threading

sys.path.append("./")
from base import message as m
from base import network

PY_NETWORK = 31000
GD_NETWORK = 32000

net_py = network.Net(get_port=PY_NETWORK, set_ports=[PY_NETWORK])
net_gd = network.Net(
    get_port=GD_NETWORK, set_ports=[GD_NETWORK], serialization_type="json"
)

stop_event = threading.Event()

TX_MSGS = [m.Coord, m.PhotoOn, m.PhotoOff]
RX_MSGS = [m.ImageLink, m.TestMessage]


def tx_thread(stop):
    global net_py
    global net_gd

    while net_py.receive() and not stop.is_set():
        if type(net_py.msg) in TX_MSGS:
            net_gd.send(net_py.msg)


def rx_thread(stop): 
    global net_py
    global net_gd

    while net_gd.receive() and not stop.is_set():
        if type(net_gd.msg) in RX_MSGS:
            net_py.send(net_gd.msg)


def main():
    rx = threading.Thread(target=rx_thread, args=(stop_event, ))
    rx.start()

    try:
        tx_thread(stop_event)
    except KeyboardInterrupt:
        stop_event.set()

    rx.join()


if __name__ == "__main__":
    main()
