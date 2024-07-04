import time

from base import network, message
from actions import key


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
                        orange_count: int):
    """
    Enables red and green LEDs according to the rules, drops the ball.
    :param object_order: list of 'triangle' and 'square' strings; shall contain only yellow objects
    :param object_interval: after detected object ignore next ones for this amount of time
    :param object_green_led: name of object to enable green leds
    :param object_red_led: name of object to enable red leds
    :param ball_drop_delay: delay after red led to drop ball
    :param orange_count: amount of orange objects before black
    :return:
    """
    green_led_counter = 0

    last_object_time = -1000

    was_red_led = False
    was_ball_drop = False
    red_led_time = 1000

    net = network.Net(timer=0.25)
    while net.receive():
        if (net.id == "Timer" and was_red_led and not was_ball_drop
                and time.time() - red_led_time > ball_drop_delay):
            drop_ball()
            was_ball_drop = True

        if net.id == message.DetectedObject.id:
            if time.time() - last_object_time < object_interval:
                continue

            if net.msg.obj == object_red_led and not was_red_led and orange_count == green_led_counter:
                ping_red_led()
                was_red_led = True
                red_led_time = time.time()

            if net.msg.obj == object_green_led:
                ping_green_led()
                if green_led_counter > len(object_order) or object_order[green_led_counter] == 'triangle':
                    # Do triangle shit I guess
                    pass
                elif object_order[green_led_counter] == 'square':
                    # Do square shit I guess
                    pass
                green_led_counter += 1

            if net.msg.obj in [object_green_led, object_red_led]:
                last_object_time = time.time()

