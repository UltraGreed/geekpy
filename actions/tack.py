import time

from base import mat, message, network
from base.message import YAW, X, Y

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25


# Robot ahead moving function with given yaw
def tack(mode='Relative', has_target=False, yaw=0.0, dist=0.1, speed=0.1, dt=None, depth=None):
    start_time = time.time()

    if not mat.is_num(dist) and not mat.is_num(dt):
        raise Exception('dist is None and dt is None')

    # Initial and current robot positions and objects data.
    start = network.wait_message('Coord').pos
    pos   = network.wait_message('Coord').pos

    # Read target yaw.
    if mode == 'Absolute':           # Use given yaw as absolute target yaw
        target_yaw = yaw
    elif mode == 'Relative':         # Use given yaw as delta to current yaw
        target_yaw = yaw + pos[YAW]
    else:                            # Set direction to object as target yaw
        if has_target:
            raise "Tack shouldn't have both target and object at the same time"
        obj   = network.wait_message('FilteredObjects').objs[mode]
        target_yaw = mat.direction(pos, obj)  # and save target yaw.

    target_yaw_old = target_yaw

    # Infinite loop until reach destination.
    net = network.Net(timer=TIMER)  # Wait for timer or message.
    while net.receive():            # Wait for timer ticks and messages.
        if net.id == 'Timer':                           # If timer tick occurs then:
            d = mat.dist2d(start, pos)                  # Calc distance
            net.send(message.Tack(time=1.0,             # Control time.speed_x=0.0,  # Send 'Tack'
                                  speed_y=speed,        # message to
                                  stab_depth=depth,     # regulator
                                  stab_yaw=target_yaw,  # with all
                                  stab_pitch=0.0,       # calculated
                                  stab_roll=0.0))       # parameters.

            if mat.is_num(dt) and time.time() > start_time + dt: return

            if mat.is_num(dist) and d > dist: return                         # If work done => exit.

        elif net.id == 'Coord':  # If coordinates has come
            pos = net.msg.pos    # then save robot position.

        elif net.id == 'Target' and has_target:
            if net.msg.is_detected:
                target_yaw = pos[YAW] + net.msg.offset_yaw
            else:
                target_yaw = target_yaw_old  # TODO: choose either reset to initial or keep old value
