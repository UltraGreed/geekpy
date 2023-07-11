#!python3
# @todo: need save only necessary position values (if is_number)!
# @todo: need filtration and avg!!!
import sys, setproctitle, time
from base import network, message, mat

TIMER   = 0.25  # Filtered objects publication timer.
TIMEOUT = 5.00  # Timeout of old data.

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net    = network.Net(timer=TIMER)              # Will send/receive some messages and wait timer ticks.
out    = message.FilteredObjects()             # Sended array with all filtered objects.
ini    = message.FilteredObjects()             # Initial array with objects coordinates.
update = message.FilteredObjects().objs        # Update time of all coord each object.

# Wait for messages or timer.
while net.receive():

    if net.id == 'Timer':                                   # If timer has come then
        for obj in update:                                  # For all objects
            for i in range(message.YAW):                    # and all axis:
                if time.time() - update[obj][i] > TIMEOUT:  # if value is old
                    out.objs[obj][i] = ini.objs[obj][i]     # then change to initial value.
        net.send(out)                                       # Send output objects array.

    elif net.id == 'DetectedObject':               # If object has come
        msg = net.msg                              # then read message.
        for i in range(len(msg.pos)):              # For all axis:
            if mat.is_num(msg.pos[i]):             # if position in axel is number
                out.objs[msg.obj][i] = msg.pos[i]  # then save to output data.
                update[msg.obj][i] = time.time()   # Update time of each value.

    elif net.id == 'ResetObjects':       # If ResetObjects message has come
        out = message.FilteredObjects()  # then save object to output array.
