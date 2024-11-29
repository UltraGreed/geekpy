import time

from base import network, message
from base.message import YAW
from actions import key
from actions.stab import stab
from actions.tack import tack


def object_reaction_akva24(
    object_down: str,
    object_up: str,
    lower_depth: float,
    upper_depth: float,
    start_depth: float,
    # exit_count: float,
):
    current_depth = start_depth
    # count = 0
    net = network.Net(timer=0.25)
    while net.receive():
        # if count == exit_count:
        #     photosave.start("Front", None)
        #     detection.on("Target")
        #     break
            
        if net.id == "Timer":
            print(current_depth)
            net.send(message.Tack(
                time=1.0,
                stab_depth=current_depth,
            ))

        if net.id == message.DetectedObject.id:
            print(net.msg.obj)
            if net.msg.obj == object_down:
                # count += 1
                current_depth = lower_depth

            if net.msg.obj == object_up:
                # count += 1
                current_depth = upper_depth
