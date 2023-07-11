# @todo: Need to make lead_distance instead radius & wait time.
import math, sys
sys.path.append('../base')
import mat, network, message
from message import X, Y, YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25

## Robot ahead moving function with given yaw
def move_object(origin='', radius=1.0, speed=0.1, depth=None):

    # Initial and current robot positions and objects data.
    pos   = network.wait_message('Coord').pos
    obj   = network.wait_message('FilteredObjects').objs[origin]

    # Infinit loop until reach destination.
    net = network.Net(timer=TIMER)  # Wait for timer or message.
    while net.receive():            # Wait for timer ticks and messages.
        
        # Send Tacks on timer and check conditions.
        if net.id == 'Timer':
            yaw = mat.direction(pos, obj)                      # Calculate robot yaw to object position.
            net.send(message.Tack(                             # Send Tack message
                time=1.0,                                      # with this timeout
                speed_x=0.0, speed_y=speed, stab_depth=depth,  # lateral and
                stab_yaw=yaw, stab_pitch=0.0, stab_roll=0.0))  # angular values.
            if mat.dist2d(pos, obj) < radius:                  # If distance too short
                return                                         # then exit forever.

        # Save robot position.
        elif net.id == 'Coord':
            pos = net.msg().pos

        # Save objects position.
        elif net.id == 'FilteredObjects':
            obj = net.msg().objs[origin]
