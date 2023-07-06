import math, sys, time
sys.path.append('../base')
import mat, network, message
from message import X, Y, YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25

## Robot ahead moving function with given yaw
def stab_xy(origin='Current', x=0.0, y=0.0, yaw=None, dt=0.0, depth=None):

    # Initial objects positions and objects data.
    objs = network.wait_message('FilteredObjects').objs
    start_time = time.time()

    # Read stab parameters.
    if origin == 'Navigation':
        stab_x = x
        stab_y = y
    elif origin == 'Current':
        pos    = network.wait_message('Coord').pos
        stab_x = x + pos[X]
        stab_y = y + pos[Y]
    else:
        stab_x = x + objs[origin][X]
        stab_y = y + objs[origin][Y]

    # Infinit loop until reach destination time.
    net = network.Net(timer=TIMER)
    while net.receive():

        # If timer tick occures then:
        if net.id() == 'Timer':                             
            # Update stab parameters if necessary.
            # Send 'Tack'
            net.send(message.Tack(time       = 1.0,    
                                  stab_x     = stab_x,      # Send 'Tack'
                                  stab_y     = stab_y,      # message to
                                  stab_depth = depth,       # regulator
                                  stab_yaw   = yaw,         # with all
                                  stab_pitch = 0.0,         # clculated
                                  stab_roll  = 0.0))        # parameters.
            # If work done => exit.
            if time.time() > start_time + dt:
                return                         

        elif net.id() == 'FilterdObjects':
            if origin == 'Navigation':
                pass
            elif origin == 'Current':
                pass
            else:
                objs = net.msg().objs
                stab_x = x + objs[origin][X]
                stab_y = y + objs[origin][Y]

