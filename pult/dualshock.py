# Use pygame to get readouts from a ds4 controller
# This is an efficient way to get inputs as long as you don't need six-axis data
import time

import pygame
import os

from base import message, network


pygame.init()
pygame.joystick.init()

controller = pygame.joystick.Joystick(0)
controller.init()

# Three types of controls: axis, button, and hat
axis = [0.0 for _ in range(controller.get_numaxes())]
button = [False for _ in range(controller.get_numbuttons())]
hat = [(0, 0) for _ in range(controller.get_numhats())]

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

# Labels for DS4 controller hats (Only one hat control)
HAT_1 = 0

send_interval = 0.1
threshold = 0.1

yaw_coef = 50
xy_coef = 10
depth_coef = 10

net = network.Net()  # TODO: msg?

# Main loop, one can press the PS button to break
while True:
    # Get events
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            axis[event.axis] = round(event.value, 3)
        elif event.type == pygame.JOYBUTTONDOWN:
            button[event.button] = True
        elif event.type == pygame.JOYBUTTONUP:
            button[event.button] = False
        elif event.type == pygame.JOYHATMOTION:
            hat[event.hat] = event.value

    tack_params = {'speed_yaw': (axis[AXIS_R2] - axis[AXIS_L2]) * yaw_coef}

    # Sticks are not ideal, so we have to use this
    if abs(axis[AXIS_LEFT_STICK_X]) > 0.1:
        tack_params['speed_x'] = axis[AXIS_LEFT_STICK_X] * xy_coef
    else:
        tack_params['speed_x'] = 0.0

    if abs(axis[AXIS_LEFT_STICK_Y]) > 0.1:
        tack_params['speed_y'] = -axis[AXIS_LEFT_STICK_Y] * xy_coef
    else:
        tack_params['speed_y'] = 0.0

    if abs(axis[AXIS_RIGHT_STICK_Y]) > 0.1:
        tack_params['speed_depth'] = -axis[AXIS_RIGHT_STICK_Y] * depth_coef
    else:
        tack_params['speed_depth'] = 0.0

    net.send(message.Tack(priority=2, time=0.1, **tack_params))

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

    print("L2 strength:", axis[AXIS_L2])
    print("R2 strength:", axis[AXIS_R2], "\n")
    # Buttons
    print("L1:", button[BUTTON_L1])
    print("R1:", button[BUTTON_R1])

    print("L2:", button[BUTTON_L2])
    print("R2:", button[BUTTON_R2])

    print("PS:", button[BUTTON_PS])

    time.sleep(send_interval)
