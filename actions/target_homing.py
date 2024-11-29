from base import network, message
from actions.tack import tack


def target_homing(depth: float, speed: float):
    """
    Listen to Target message and answer with corresponding Tack.

    :param depth: depth of Tack message
    :param speed: speed of Tack message
    :return:
    """
    net = network.Net(timer=0.25)
    while net.receive():
        if net.id == message.Target and net.msg.is_detected:
            tack(
                priority=1,
                mode='Relative',
                depth=depth,
                dt=1,
                speed=speed,
                yaw=net.msg.offset_yaw,
            )
