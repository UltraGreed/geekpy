#!python3
# @todo: Need to fix bag with InitRobot offset.
import sys, setproctitle
from base import mat, network, message
from base.message import AXIS

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net    = network.Net()                         # Will send/receive some messages and wait timer ticks.
coord  = message.Coord()                       # Sended message to all progs.
offset = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]        # Position offset from current sensor data.

# Wait for messages or timer
while net.receive():
    if net.id == 'Sensor':                         # If sensor data has come
        msg = net.msg                              # then read sensor message
        pos, vel, acc = msg.pos, msg.vel, msg.acc  # and save necessary data.
        for i in range(AXIS):                      # For all axis
            if mat.is_num(pos[i]):                 # correct
                coord.pos[i] = pos[i] - offset[i]  # position,
            if mat.is_num(vel[i]):                 # apply
                coord.vel[i] = vel[i]              # velocity
            if mat.is_num(acc[i]):                 # and
                coord.acc[i] = acc[i]              # acceleration.
        net.send(coord)                            # Send message to consumers.

    elif net.id == 'InitRobot':                    # If Initialization message has come
        pos = net.msg.pos                          # then save position
        for i in range(AXIS):                      # and for each axel
            if mat.is_num(pos[i]):                 # (if input value is number)
                offset[i] = coord.pos[i] - pos[i]  # calculate offset.
