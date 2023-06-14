import math, sys
sys.path.append('../base')
import mat, network, message
from message import X, Y, YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.5

## Robot ahead moving function with given yaw
def ahead(origin='Current', yaw=0, dist=1, speed=0.1, depth=0):

    # Initial and current robot positions and objects data.
    pos   = network.wait_message('Coord').pos
    start = network.wait_message('Coord').pos
    objs  = network.wait_message('FilteredObjects')

    # Read target yaw.
    target_yaw = None
    if origin == 'Navigation':                # Navigation yaw
        target_yaw = yaw                      # = yaw from param.
    elif origin == 'Current':                 # Current yaw
        target_yaw = yaw + pos[YAW]           # = yaw + current robot yaw.
    else:                                     # If origin object is necessary
        target_yaw = yaw + objs[origin][YAW]  # and save target yaw.

    # Infinit loop until reach destination.
    net = network.Net(timer=TIMER)                          # Wait for timer or message.
    while net.receive():                                    # Wait for timer ticks and messages.
        if net.id() == 'Timer':                             # If timer tick occures then:
            d = math.sqrt((start[X] - pos[X])**2            # Calc distance
                        + (start[Y] - pos[Y])**2)           # from start.
            net.send(message.Tack(speed_x    = 0.0,         # Send 'Tack'
                                  speed_y    = speed,       # message to
                                  stab_depth = depth,       # regulator
                                  stab_yaw   = target_yaw,  # with all
                                  stab_pitch = 0.0,         # clculated
                                  stab_roll  = 0.0))        # parameters.
            if d > dist: return                             # If work done => exit.
        elif net.id() == 'Coord':                           # If coordinates has come
            pos = net.msg().pos                             # then save robot position.
