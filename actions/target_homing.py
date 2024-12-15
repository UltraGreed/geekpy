from base import network, message
from base.message import YAW
import time


def target_homing(depth: float, speed: float, timeout: float):
    """
    Listen to Target message and answer with corresponding Tack.

    :param depth: depth of Tack message
    :param speed: speed of Tack message
    :return:
    """
    pos = network.wait_message('Coord').pos
    target_yaw = pos[YAW]
    time_start = time.time()
    net = network.Net(timer=0.25)
    while net.receive():
        if net.id == 'Timer':
            if time.time() - time_start > timeout:
                break

            net.send(message.Tack(
                time=1,
                speed_y=speed,
                speed_x=0,
                stab_depth=depth,
                stab_yaw=target_yaw,
                stab_pitch=0.0,
                stab_roll=0.0
            ))

        if net.id == message.Target.id:
            if net.msg.is_detected:
                target_yaw = net.msg.offset_yaw + pos[YAW]
            else:
                target_yaw = pos[YAW]

        if net.id == message.Coord.id:
            pos = net.msg.pos
