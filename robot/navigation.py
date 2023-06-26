#!python3 navigation.py
# @todo: Need to fix bag with InitRobot offset.
import sys

import setproctitle

sys.path.append('./')
from base import mat, message, network
from base.message import AXIS

TIMER = 0.05  # Coordinates publication timer.

setproctitle.setproctitle(sys.argv[0])   # Set filename.py title for process.
net    = network.Net(timer=TIMER)        # Will send/receive some messages and wait timer ticks.
coord  = message.Coord()                 # Sended message to all progs.
offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Position offset from current sensor data.

while net.receive():  # Wait for messages or timer

    if net.id() == 'Timer':  # If timer has come
        net.send(coord)      # then send message to consumers.

    elif net.id() == 'Sensor':                     # If sensor data has come
        msg = net.msg()                            # then read sensor message
        pos, vel, acc = msg.pos, msg.vel, msg.acc  # and save necessary data.
        for i in range(AXIS):                                         # For all axis
            if mat.is_num(pos[i]): coord.pos[i] = pos[i] - offset[i]  # correct position,
            if mat.is_num(vel[i]): coord.vel[i] = vel[i]              # apply velocity
            if mat.is_num(acc[i]): coord.acc[i] = acc[i]              # and acceleration.

    elif net.id() == 'InitRobot':   # If Initialization message has come
        pos = net.msg().pos         # then save position
        for i in range(AXIS):       # and calculate offset
            if mat.is_num(pos[i]):  # (if input value is number).
                offset[i] = coord.pos[i] - pos[i]
