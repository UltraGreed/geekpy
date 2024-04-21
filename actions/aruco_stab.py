import math, sys, time
from base import mat, network, message
from base.message import X, Y, YAW

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25


## Robot ahead moving function with given yaw
def aruco_stab(right=0.0, front=0.0, dt=0.0, depth=None):

    # Initial objects positions and objects data.
    start_time = time.time()

    origin = "Aruco"

    objs = network.wait_message("FilteredObjects").objs

    yaw = objs[origin][YAW]

    dx, dy = mat.rotate2map(-right, -front, yaw)
    stab = [objs[origin][X] + dx, objs[origin][Y] + dy]

    # Infinit loop until reach destination time.
    net = network.Net(timer=TIMER)
    while net.receive():

        # If timer tick occures then:
        if net.id == "Timer":
            net.send(
                message.Tack(
                    time=1.0,  # Send 'Tack'
                    stab_x=stab[X],  # message
                    stab_y=stab[Y],  # to
                    stab_depth=depth,  # regulator
                    stab_yaw=yaw,  # with all
                    stab_pitch=0.0,  # clculated
                    stab_roll=0.0,
                )
            )  # parameters.
            if time.time() > start_time + dt:  # If work done
                return  # then exit.

        # If filtered objects has come, then update stab point.
        elif net.id == "FilteredObjects":
            objs = net.msg.objs
            yaw = objs[origin][YAW]
            dx, dy = mat.rotate2map(-right, -front, yaw)
            stab = [objs[origin][X] + dx, objs[origin][Y] + dy]
