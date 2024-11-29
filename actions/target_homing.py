from base import network, message
from base.message import YAW


def target_homing(depth: float, speed: float):
    """
    Listen to Target message and answer with corresponding Tack.

    :param depth: depth of Tack message
    :param speed: speed of Tack message
    :return:
    """
    pos = network.wait_message('Coord').pos
    net = network.Net(timer=0.25)
    while net.receive():
        if net.id == message.Target.id and net.msg.is_detected:
            net.send(message.Tack(
                time=0.5,
                speed_y=speed,
                speed_x=0,
                stab_depth=depth,
                stab_yaw=net.msg.offset_yaw + pos[YAW],
                stab_pitch=0.0,
                stab_roll=0.0
            ))

        if net.id == message.Coord.id:
            pos = net.msg.pos
