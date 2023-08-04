# Use pygame to get readouts from a ds4 controller
# This is an efficient way to get inputs as long as you don't need six-axis data

import time

import pygame
import os
import sys

import setproctitle

from base import message, network
from base.message import X, Y, DEPTH, YAW, PITCH, ROLL

############################
# Configuration parameters #
THRESHOLD = 0.1

X_COEF = 0.15
Y_COEF = 0.6

Y_STEP = 0.02
X_STEP = 0.008

DEPTH_COEF = 0.15
YAW_COEF = 60

PITCH_COEF = 45
ROLL_COEF = 60

STAB_X_STEP = 0.05
STAB_Y_STEP = 0.05

STAB_DEPTH_SMALL_STEP = 0.02
STAB_DEPTH_BIG_STEP = 0.20
STAB_YAW_SMALL_STEP = 2
STAB_YAW_BIG_STEP = 8

STAB_PITCH_COEF = 30
STAB_ROLL_COEF = 90

UPDATE_FREQ = 10

DEBUG = False
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

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net = network.Net(timer=1 / UPDATE_FREQ)  # TODO: msg?

is_stab_yaw = False
is_stab_xy = False
is_stab_depth = False
is_stab_pitch = True
is_stab_roll = True

pos_x, pos_y, pos_depth, pos_yaw, pos_pitch, pos_roll = 0, 0, 0, 0, 0, 0
stab_x, stab_y, stab_depth, stab_yaw, stab_pitch, stab_roll = 0, 0, 0, 0, 0, 0

speed_depth = 0
speed_pitch = 0
speed_roll = 0

is_paused = False

# Main loop
while net.receive():
    if net.id == "Timer":
        button_click = [False for _ in range(controller.get_numbuttons())]
        was_input = False
        # Get events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                axis[event.axis] = round(event.value, 3)
                if abs(event.value) > THRESHOLD:
                    was_input = True
            elif event.type == pygame.JOYBUTTONDOWN:
                button[event.button] = True
                button_click[event.button] = True
                was_input = True
            elif event.type == pygame.JOYBUTTONUP:
                button[event.button] = False
            elif event.type == pygame.JOYHATMOTION:
                hat = event.value
                was_input = True

        speed_x = 0
        speed_y = 0
        speed_depth = 0
        speed_yaw = 0
        stab_pitch = 0
        stab_roll = 0

        if button[BUTTON_TRIANGLE]:
            if is_stab_depth:
                stab_depth -= STAB_DEPTH_SMALL_STEP
            else:
                is_stab_depth = True
                stab_depth = pos_depth - STAB_DEPTH_SMALL_STEP

        if button[BUTTON_CROSS]:
            if is_stab_depth:
                stab_depth += STAB_DEPTH_SMALL_STEP
            else:
                is_stab_depth = True
                stab_depth = pos_depth + STAB_DEPTH_SMALL_STEP

        if button[BUTTON_SQUARE]:
            speed_x -= X_STEP * UPDATE_FREQ

        if button[BUTTON_CIRCLE]:
            speed_x += X_STEP * UPDATE_FREQ

        if hat[0]:
            if is_stab_yaw:
                stab_yaw += STAB_YAW_SMALL_STEP * hat[0]
            else:
                is_stab_yaw = True
                stab_yaw = pos_yaw + STAB_YAW_SMALL_STEP * hat[0]

        if hat[1]:
            speed_y += Y_STEP * UPDATE_FREQ * hat[1]

        if abs(axis[AXIS_LEFT_STICK_X]) > THRESHOLD:
            is_stab_yaw = False
            speed_yaw = YAW_COEF * axis[AXIS_LEFT_STICK_X]
        else:
            speed_yaw = 0.0

        if abs(axis[AXIS_LEFT_STICK_Y]) > THRESHOLD:
            speed_y = -axis[AXIS_LEFT_STICK_Y] * Y_COEF

        # Sticks are not ideal, so we have to use thresholds
        if abs(axis[AXIS_RIGHT_STICK_X]) > THRESHOLD:
            speed_x = axis[AXIS_RIGHT_STICK_X] * X_COEF

        # If stabilization is enabled or input given, we calculate stabilization
        if is_stab_pitch or abs(axis[AXIS_RIGHT_STICK_Y]) > THRESHOLD:
            is_stab_pitch = True
            stab_pitch = -axis[AXIS_RIGHT_STICK_Y] * STAB_PITCH_COEF

        # If stabilization is enabled or input given, we calculate stabilization
        # if is_stab_roll or axis[AXIS_R2] != axis[AXIS_L2]:
        #     is_stab_roll = True
        #     stab_roll = (axis[AXIS_R2] - axis[AXIS_L2]) / 2 * STAB_ROLL_COEF

        if button[BUTTON_L1]:
            is_stab_depth = False
            speed_depth -= DEPTH_COEF

        if axis[AXIS_L2] != -1:
            is_stab_depth = False
            speed_depth += DEPTH_COEF * (1 + axis[AXIS_L2]) / 2

        if button[BUTTON_R1]:
            net.send(message.KeyOn('Close', (1 / UPDATE_FREQ) * 1.1))

        if axis[AXIS_R2] == 1:
            net.send(message.KeyOn('Open', (1 / UPDATE_FREQ) * 1.1))

        tack_params = {
            'speed_x': speed_x if not is_stab_xy else None,
            'speed_y': speed_y if not is_stab_xy else None,
            'speed_depth': speed_depth if not is_stab_depth else None,
            'speed_yaw': speed_yaw if not is_stab_yaw else None,
            'speed_pitch': speed_pitch if not is_stab_pitch else None,
            'speed_roll': speed_roll if not is_stab_roll else None,
            'stab_x': stab_x if is_stab_xy else None,
            'stab_y': stab_y if is_stab_xy else None,
            'stab_depth': stab_depth if is_stab_depth else None,
            'stab_yaw': stab_yaw if is_stab_yaw else None,
            'stab_pitch': stab_pitch if is_stab_pitch else None,
            'stab_roll': stab_roll if is_stab_roll else None,
        }

        if was_input or not is_paused:
            is_paused = False
            net.send(message.Tack(priority=2, time=1, **tack_params))

        # Disable stabilisation
        if button[BUTTON_PS]:
            is_stab_x = False
            is_stab_y = False
            is_stab_depth = False
            is_stab_yaw = False
            # is_stab_pitch = False
            # is_stab_roll = False

        # Reset xy coordinates
        if button[BUTTON_SHARE]:
            init = message.InitRobot(x=0, y=0)
            net.send(init)

        # Reset xy, yaw and depth
        if button[BUTTON_OPTIONS]:
            # init = message.InitRobot(x=0, y=0, yaw=0, depth=0)
            # net.send(init)
            is_paused = True

        if DEBUG:
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
    elif net.id == "Coord":
        pos_x = net.msg.pos[X]
        pos_y = net.msg.pos[Y]
        pos_depth = net.msg.pos[DEPTH]
        pos_yaw = net.msg.pos[YAW]
        pos_pitch = net.msg.pos[PITCH]
        pos_roll = net.msg.pos[ROLL]

