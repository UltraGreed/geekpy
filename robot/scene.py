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

    if net.id() == 'Timer':  # If timer has come then
        net.send(out)        # send output objects array.

    elif net.id() == 'DetectedObject':  # If object has come
        data = net.msg()                # then read object position
        out.objs[data.obj] = data.pos   # and save to filtered output data.

    elif net.id() == 'ResetObjects':     # If ResetObjects message has come
        out = message.FilteredObjects()  # then save object to output array.
