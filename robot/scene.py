#!python3 scene.py
import sys, setproctitle
sys.path.append('../base')
import mat, network, message
# from message import AXIS

TIMER = 0.3  # Coordinates publication timer.

setproctitle.setproctitle(sys.argv[0])  # Set filename.py title for process.
net = network.Net(timer=TIMER)          # Will send/receive some messages and wait timer ticks.
pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]    # Input robot position.
out = message.FilteredObjects()         # Sended array with all filtered objects.

while net.receive():  # Wait for messages or timer

    if net.id == 'Timer':  # If timer has come then
        net.send(out)        # send output objects array.

    # elif net.id == 'Coord':  # If Coord data has come
    #     pos = net.msg().pos    # then save robot position.

    # elif net.id == 'InitObject':               # If Initialization message has come
    #     out.objs[net.msg().obj] = net.msg().pos  # then save object to output array.
