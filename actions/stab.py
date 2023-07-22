import math, sys, time
from base import mat, network, message
from base.message import X, Y, YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25

## Robot ahead moving function with given yaw
def stab(origin='Current', x=0.0, y=0.0, left=0.0, front=0.0, yaw=None, dt=0.0, depth=None):

    # Initial objects positions and objects data.
    start_time = time.time()

    # Read stab parameters.
    stab = None
    if origin == 'Navigation':
        stab = [x, y]
    elif origin == 'Current':
        pos  = network.wait_message('Coord').pos
        stab = [x + pos[X], y + pos[Y]]
    else:
        objs = network.wait_message('FilteredObjects').objs
        stab = [x + objs[origin][X], y + objs[origin][Y]]

    # Infinit loop until reach destination time.
    net = network.Net(timer=TIMER)
    while net.receive():

        # If timer tick occures then:
        if net.id == 'Timer':                             
            net.send(message.Tack(time       = 1.0,      # Send 'Tack'
                                  stab_x     = stab[X],  # message
                                  stab_y     = stab[Y],  # to
                                  stab_depth = depth,    # regulator
                                  stab_yaw   = yaw,      # with all
                                  stab_pitch = 0.0,      # clculated
                                  stab_roll  = 0.0))     # parameters.
            if time.time() > start_time + dt:            # If work done
                return                                   # then exit.

        # If filtered objects has come, then update stab point.
        elif net.id == 'FilteredObjects':
            if origin != 'Navigation' and origin != 'Current':
                objs = net.msg.objs
                stab = [x + objs[origin][X], y + objs[origin][Y]]

