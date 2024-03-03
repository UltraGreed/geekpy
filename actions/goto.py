# @todo: Need to make lead_distance instead radius & wait time.
from base import mat, network, message

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25


# Robot ahead moving function with given yaw
def goto(origin='', radius=1.0, speed=0.1, hold_time=0.0, depth=None):
    timer = 0.0

    # Initial and current robot position
    auv_pos = network.wait_message('Coord').pos

    # Either get object coords or use given coords
    is_obj_oriented = origin is tuple
    if is_obj_oriented:
        target_pos = network.wait_message('FilteredObjects').objs[origin]
    else:
        target_pos = origin

    # Infinite loop until auv reaches destination.
    net = network.Net(timer=TIMER)  # Wait for timer or message.
    while net.receive():            # Wait for timer ticks and messages.
        # if auv is far from target
        if net.id == 'Timer' and mat.dist2d(auv_pos, target_pos) > radius:
            yaw = mat.direction(auv_pos, target_pos)  # Calculate relative yaw to object position.
            net.send(message.Tack(
                time=1.0,
                speed_x=0.0, speed_y=speed,
                stab_depth=depth, stab_yaw=yaw, stab_pitch=0.0, stab_roll=0.0
            ))

        # if auv is close to target
        if net.id == 'Timer' and mat.dist2d(auv_pos, target_pos) <= radius:
            timer += TIMER   # time when auv is close to target
            net.send(message.Tack(
                time=1.0,
                speed_x=0.0, speed_y=0.0,
                stab_depth=depth, stab_yaw=None, stab_pitch=0.0, stab_roll=0.0
            ))
            if timer >= hold_time:
                return

        # Save robot position.
        elif net.id == 'Coord':
            auv_pos = net.msg.pos

        # Change object position.
        elif net.id == 'FilteredObjects' and is_obj_oriented:
            target_pos = net.msg.objs[origin]
