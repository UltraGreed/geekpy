#!python3
# @todo: need save only necessary position values (if is_number)!
# @todo: need filtration and avg!!!
import setproctitle
import sys
import time

from base import network, message, mat

# from message import AXIS

TIMER   = 0.25  # Filtered objects publication timer.
DEFAULT_TIMEOUT = 10.0

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net    = network.Net(timer=TIMER)              # Will send/receive some messages and wait timer ticks.
out    = message.FilteredObjects()             # Sended array with all filtered objects.
ini    = message.FilteredObjects()             # Initial array with objects coordinates.
update = message.FilteredObjects().objs        # Update time of all coord each object.

is_detection_on = {} # if object must be detected
for key in ini.objs:
    is_detection_on[key] = False

timeout_for_on = {} # then set timeout to this value
for key in ini.objs:
    timeout_for_on[key] = DEFAULT_TIMEOUT

timeout_for_off = {} # else to this value
for key in ini.objs:
    timeout_for_off[key] = DEFAULT_TIMEOUT

# Wait for messages or timer.
while net.receive():

    if net.id == 'Timer':                                   # If timer has come then
        for obj in update:                                  # For all objects
            for i in range(message.YAW):                    # and all axis:
                                                            # if value is old
                                                            # then change to initial value.

                if is_detection_on[obj] and time.time() - update[obj][i] > timeout_for_on[obj]:
                    out.objs[obj][i] = ini.objs[obj][i]
                elif not is_detection_on[obj] and time.time() - update[obj][i] > timeout_for_off[obj]:
                    out.objs[obj][i] = ini.objs[obj][i]
        net.send(out)                                       # Send output objects array.

    elif net.id == 'DetectedObject':               # If object has come
        msg = net.msg                              # then read message.
        for i in range(len(msg.pos)):              # For all axis:
            if msg.pos[i] is not None:             # if position in axel is number
                out.objs[msg.obj][i] = msg.pos[i]  # then save to output data.
                update[msg.obj][i] = time.time()   # Update time of each value.

    elif net.id == 'ResetObjects':       # If ResetObjects message has come
        out = message.FilteredObjects()  # then save object to output array.

    elif net.id == 'DetectionOn':
        is_detection_on[net.msg.obj] = True 
        timeout_for_on[net.msg.obj] = net.msg.timeout

    elif net.id == 'DetectionOff':
        is_detection_on[net.msg.obj] = False
        timeout_for_off[net.msg.obj] = net.msg.timeout
