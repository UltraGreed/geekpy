import time

from base import mat, network, message
from base.message import X, Y, YAW

from base.config import MAIN_TIMER

# Timer period to send 'Tack' message to regulator.


## Robot ahead moving function with given yaw
def stab(
    origin="Current", x=0.0, y=0.0, right=0.0, front=0.0, yaw=None, dt=0.0, depth=None, priority=0
):
    is_object_yaw = False

    stab = None
    if origin == "Navigation":
        stab = [x, y]
    elif origin == "Current":
        pos = network.wait_message("Coord").pos
        stab = [x + pos[X], y + pos[Y]]
    else:
        objs = network.wait_message("FilteredObjects").objs

        if yaw is None:
            yaw = network.wait_message("Coord").pos[YAW]
        elif yaw == "Object":
            is_object_yaw = True
            yaw = objs[origin][YAW]

        dx, dy = mat.rotate2map(-right, -front, yaw)
        stab = [x + objs[origin][X] + dx, y + objs[origin][Y] + dy]

    start_time = time.time()

    net = network.Net(timer=MAIN_TIMER)
    while net.receive():

        if net.id == "Timer":
            net.send(
                message.Tack(
                    priority=priority,
                    time=1.0,
                    stab_x=stab[X],
                    stab_y=stab[Y],
                    stab_depth=depth,
                    stab_yaw=yaw,
                    stab_pitch=0.0,
                    stab_roll=0.0,
                )
            )
            if time.time() > start_time + dt:
                return

        elif net.id == "FilteredObjects":
            if origin != "Navigation" and origin != "Current":
                objs = net.msg.objs

                if is_object_yaw:
                    yaw = objs[origin][YAW]

                dx, dy = mat.rotate2map(-right, -front, yaw)
                stab = [x + objs[origin][X] + dx, y + objs[origin][Y] + dy]
