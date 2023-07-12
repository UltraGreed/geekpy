# Use pygame to get readouts from a ds4 controller
# This is an efficient way to get inputs as long as you don't need six-axis data

import time

import pygame
import os

from base import message, network
from base.message import X, Y, DEPTH, YAW


############################
# Configuration parameters #
threshold = 0.1

xy_coef = 1
depth_coef = 0.5
yaw_coef = 50

stab_xy_step = 5
stab_depth_step = 0.1
stab_yaw_step = 90
############################

pygame.init()
pygame.joystick.init()

controller = pygame.joystick.Joystick(0)
controller.init()

# Three types of controls: axis, button, and hat
axis = [0.0 for _ in range(controller.get_numaxes())]
button = [False for _ in range(controller.get_numbuttons())]
hat = (0, 0)

# Labels for DS4 controller axes
AXIS_LEFT_STICK_X = 0
AXIS_LEFT_STICK_Y = 1
AXIS_RIGHT_STICK_X = 3
AXIS_RIGHT_STICK_Y = 4
AXIS_R2 = 5
AXIS_L2 = 2

# For some reason this is their actual default state
axis[AXIS_R2], axis[AXIS_L2] = -1, -1

# Labels for DS4 controller buttons
# Note that there are 14 buttons (0 to 13 for pygame, 1 to 14 for Windows setup)
BUTTON_CROSS = 0
BUTTON_CIRCLE = 1
BUTTON_TRIANGLE = 2
BUTTON_SQUARE = 3

BUTTON_L1 = 4
BUTTON_R1 = 5
BUTTON_L2 = 6
BUTTON_R2 = 7

BUTTON_SHARE = 8
BUTTON_OPTIONS = 9

BUTTON_PS = 10

BUTTON_LEFT_STICK = 11
BUTTON_RIGHT_STICK = 12
# BUTTON_PAD = 13

net = network.Net(timer=0.1)  # TODO: msg?

is_stab_yaw = False
is_stab_x = False
is_stab_y = False
is_stab_depth = False

pos_x, pos_y, pos_depth, pos_yaw = 0, 0, 0, 0

# Main loop
while net.receive():
    if net.id == "Timer":
        button_click = [False for _ in range(controller.get_numbuttons())]
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                axis[event.axis] = round(event.value, 3)
            elif event.type == pygame.JOYBUTTONDOWN:
                button[event.button] = True
                button_click[event.button] = True
            elif event.type == pygame.JOYBUTTONUP:
                button[event.button] = False
            elif event.type == pygame.JOYHATMOTION:
                hat = event.value

        if button_click[BUTTON_R1]:
            is_stab_yaw = True
            stab_yaw = pos_yaw + stab_yaw_step

        if button_click[BUTTON_L1]:
            is_stab_yaw = True
            stab_yaw = pos_yaw - stab_yaw_step

        if button_click[BUTTON_TRIANGLE]:
            is_stab_depth = True
            stab_depth = pos_depth - stab_depth_step

        if button_click[BUTTON_CROSS]:
            is_stab_depth = True
            stab_depth = pos_depth + stab_depth_step

        # TODO: stabilization for xy
        if hat[0]:
            # is_stab_x = True
            stab_x = pos_x + stab_xy_step * hat[0]

        if hat[1]:
            # is_stab_y = True
            stab_y = pos_y + stab_xy_step * hat[1]

        # Sticks are not ideal, so we have to use this
        if abs(axis[AXIS_LEFT_STICK_X]) > threshold:
            speed_x = axis[AXIS_LEFT_STICK_X] * xy_coef
            is_stab_x = False
        else:
            speed_x = 0.0

        if abs(axis[AXIS_LEFT_STICK_Y]) > threshold:
            speed_y = -axis[AXIS_LEFT_STICK_Y] * xy_coef
            is_stab_y = False
        else:
            speed_y = 0.0

        if abs(axis[AXIS_RIGHT_STICK_Y]) > threshold:
            speed_depth = axis[AXIS_RIGHT_STICK_Y] * depth_coef
            is_stab_depth = False
        else:
            speed_depth = 0.0

        speed_yaw = (axis[AXIS_R2] - axis[AXIS_L2]) / 2 * yaw_coef
        if speed_yaw != 0:
            is_stab_yaw = False

        tack_params = {
            'speed_x': speed_x if not is_stab_x else None,
            'speed_y': speed_y if not is_stab_y else None,
            'speed_depth': speed_depth if not is_stab_depth else None,
            'speed_yaw': speed_yaw if not is_stab_yaw else None,
            'stab_x': stab_x if is_stab_x else None,
            'stab_y': stab_y if is_stab_y else None,
            'stab_depth': stab_depth if is_stab_depth else None,
            'stab_yaw': stab_yaw if is_stab_yaw else None
        }

        net.send(message.Tack(priority=2, time=1, **tack_params))

        # Resets all the values to default (debug purposes)
        if button[BUTTON_PS]:
            init = message.InitRobot()
            net.send(init)

        # Print out results
        os.system('clear')
        # Axes
        print("Left stick X:", axis[AXIS_LEFT_STICK_X])
        print("Left stick Y:", axis[AXIS_LEFT_STICK_Y])

        print("Right stick Y:", axis[AXIS_RIGHT_STICK_Y])

        print("Hat:", hat)

        print("L2 strength:", axis[AXIS_L2])
        print("R2 strength:", axis[AXIS_R2], "\n")
        # Buttons
        print("L1:", button[BUTTON_L1])
        print("R1:", button[BUTTON_R1])

        print("L2:", button[BUTTON_L2])
        print("R2:", button[BUTTON_R2])

        print("PS:", button[BUTTON_PS])
    elif net.id == "Sensor":
        if net.msg.pos[X] is not None:
            pos_x = net.msg.pos[X]

        if net.msg.pos[Y] is not None:
            pos_y = net.msg.pos[Y]

        if net.msg.pos[DEPTH] is not None:
            pos_depth = net.msg.pos[DEPTH]

        if net.msg.pos[YAW] is not None:
            pos_yaw = net.msg.pos[YAW]
