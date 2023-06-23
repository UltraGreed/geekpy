#!python3 object.py
import time, sys, setproctitle, random
sys.path.append('../base')
import network, message
from message import X, Y

# Input parameters.
X      = float(sys.argv[1])
Y      = float(sys.argv[2])
OBJ    =       sys.argv[3]
DISP   = float(sys.argv[4])
PERIOD = float(sys.argv[5])

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=PERIOD)                # Network communication.

# Send object coordinates by timer.
while net.receive():

    if net.id() == 'Timer':
        x   = X + DISP * (random.random() - random.random()) / 2
        y   = Y + DISP * (random.random() - random.random()) / 2
        msg = message.DetectedObject(obj=OBJ, x=x, y=y)
        net.send(msg)
