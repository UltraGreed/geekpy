#!python3 map.py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time, sys
sys.path.append('../base')
import mat, network, message
from message import X, Y, YAW

# Static markers coordinates.
MARKERS = {
    "Zero":       ([0],
                   [0]),
    "Pool":       ([-5,  5, -5, 5],
                   [-5, -5,  5, 5]),
    "StabSquare": ([-2,  2, -2, 2],
                   [-2, -2,  2, 2])
}

# Robot (X, Y) coordinates.
ROBOT = [( 0.0, -0.3),
         (-0.2, -0.4),
         ( 0.0,  0.4),
         ( 0.2, -0.4),
         ( 0.0, -0.3)]

REFRESH = 0.5      # Refresh time, sec.
POINTS  = 120 * 3  # Number of points in trajectories.

# matplotlib.use('TkAgg')
plt.ion()
fig = plt.figure(num='Map')
sub = fig.add_subplot(1,1,1)
sub.axis('equal')

# Init robot position&trajectory and static markers.
robot, = sub.plot([], [], '-', color='#FF330099', linewidth=2)
way,   = sub.plot([], [], '-', color='#FF330033', linewidth=1)
for m in MARKERS:
    sub.plot(MARKERS[m][X], MARKERS[m][Y], 'o', color='#00000066')

# Connect to network and start to redresh data.
net = network.Net(timer=REFRESH)
pos_x, pos_y, pos_yaw = 0.0, 0.0, 0.0
way_x, way_y = [], []
robot_x, robot_y = [0] * len(ROBOT), [0] * len(ROBOT)

# Update plots in infinit loop.
while net.receive():
    
    # Update plots on timer.
    if net.id() == 'Timer':

        # Update robot position.
        for i in range(len(ROBOT)):
            # print("i =", i, "r =", ROBOT[i])
            dx, dy = mat.robot2map(ROBOT[i][X], ROBOT[i][Y], pos_yaw)
            robot_x[i] = pos_x + dx
            robot_y[i] = pos_y + dy
        robot.set_xdata(robot_x)
        robot.set_ydata(robot_y)

        # Update robot trajectory.
        way_x = np.append(way_x, pos_x)
        way_y = np.append(way_y, pos_y)
        while len(way_x) > POINTS: way_x = way_x[1:]
        while len(way_y) > POINTS: way_y = way_y[1:]
        way.set_xdata(way_x)
        way.set_ydata(way_y)

        # Update plots.
        fig.canvas.draw()
        fig.canvas.flush_events()

    # Save robot coordinates.
    elif net.id() == 'Coord':
        pos     = net.msg().pos
        pos_x   = pos[X  ] if mat.is_num(pos[X  ]) else 0.0
        pos_y   = pos[Y  ] if mat.is_num(pos[Y  ]) else 0.0
        pos_yaw = pos[YAW] if mat.is_num(pos[YAW]) else 0.0
