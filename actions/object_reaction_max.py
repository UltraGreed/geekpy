import time

from base import network, message
from base.message import YAW
from actions import key
from actions.stab import stab
from actions.tack import tack


def drop_ball():
    print('ball dropped')
    key.on('Left', 1)


def ping_green_led():
    print('green led enabled')
    key.off('Red')
    key.on('Green', 1)


def ping_red_led():
    print('red led enabled')
    key.off('Green')
    key.on('Red', 1)


def object_reaction_min(object_order: tuple,
                        object_interval: float,
                        object_green_led: str,
                        object_red_led: str,
                        ball_drop_delay: float,
                        line_depth: float,
                        max_depth: float):
    """
    Enables red and green LEDs according to the rules, drops the ball.
    :param object_order: list of 'triangle' and 'square' strings; shall contain only yellow objects
    :param object_interval: after detected object ignore next ones for this amount of time
    :param object_green_led: name of object to enable green leds
    :param object_red_led: name of object to enable red leds
    :param ball_drop_delay: delay after red led to drop ball
    :return:
    """
    green_led_counter = 0

    last_object_time = -1000

    was_red_led = False
    was_ball_drop = False
    red_led_time = 0

    net = network.Net(timer=0.25)
    while net.receive():
        if (net.id == "Timer" and was_red_led and not was_ball_drop
                and time.time() - red_led_time > ball_drop_delay):
            drop_ball()
            was_ball_drop = True

        if net.id == message.DetectedObject.id:
            if time.time() - last_object_time < object_interval:
                continue
            if net.msg.obj == object_red_led and not was_red_led:
                ping_red_led()
                was_red_led = True
                red_led_time = time.time()

            if net.msg.obj == object_green_led:
                ping_green_led()
                yaw = network.wait_message("Coord").pos[YAW]
                if green_led_counter > len(object_order) or object_order[green_led_counter] == 'triangle':
                    # Do triangle shit I guess
                    stab(priority=1, origin=object_green_led, depth=line_depth, dt=1.0, yaw=yaw)
                    stab(priority=1, origin=object_green_led, depth=line_depth, dt=2.5, yaw=yaw + 90)
                    stab(priority=1, origin=object_green_led, depth=line_depth, dt=2.5, yaw=yaw + 180)
                    stab(priority=1, origin=object_green_led, depth=line_depth, dt=2.5, yaw=yaw + 270)
                    stab(priority=1, origin=object_green_led, depth=line_depth, dt=2.5, yaw=yaw)
                elif object_order[green_led_counter] == 'square':
                    # Do square shit I guess
                    stab(priority=1, origin=object_green_led, depth=line_depth, dt=5.0, yaw=yaw)
                    tack(priority=1, mode="Absolute", depth=max_depth, dt=10.0, dist=1.0, speed=0.0, yaw=yaw)
                    stab(priority=1, origin=object_green_led, depth=line_depth, dt=5.0, yaw=yaw)
                green_led_counter += 1

            if net.msg.obj in [object_green_led, object_red_led]:
                last_object_time = time.time()

