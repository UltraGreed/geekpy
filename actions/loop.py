import math
import time

from base import mat, message, network
from base.message import YAW, X, Y

# Timer period to send 'Tack' message to regulator.
TIMER = 0.25

## Robot ahead moving function with given yaw
def loop(yaw=0.0, pitch=0.0, roll=0.0, dt=None, depth=None):
    start_time = time.time()

    # Initial and current robot positions and objects data.
    start = network.wait_message('Coord').pos
    pos   = network.wait_message('Coord').pos

    # Infinit loop until reach destination.
    net = network.Net(timer=TIMER)  # Wait for timer or message.
    while net.receive():            # Wait for timer ticks and messages.

        if net.id == 'Timer':                           # If timer tick occures then:
            net.send(message.Tack(time=1.0,             # Control time.speed_x=0.0,  # Send 'Tack'
                                  speed_yaw=yaw,
                                  speed_pitch=pitch,
                                  speed_roll=roll,
                                  stab_depth=depth))     # regulator

            if dt is not None and time.time() > start_time + dt: return

        elif net.id == 'Coord':  # If coordinates has come
            pos = net.msg.pos    # then save robot position.
