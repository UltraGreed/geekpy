#!python3 map.py
import setproctitle
import sys

import matplotlib
import matplotlib.pyplot as plt
from base import network, mat

import numpy as np

from base.message import X, Y, YAW

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

REFRESH = 0.2      # Refresh time, sec.
POINTS  = 20 * 60  # Number of points in trajectories.

# matplotlib.use('TkAgg')
setproctitle.setproctitle(sys.argv[0])  # Set filename.py title for process.
plt.ion()
fig = plt.figure(num='Map')
sub = fig.add_subplot(1,1,1)
sub.axis('equal')

# Init robot position&trajectory and static markers.
for m in MARKERS:
    sub.plot(MARKERS[m][X], MARKERS[m][Y], '+', color='#00000066')
objs,  = sub.plot([], [], 'o', color='#00FF0033')
way,   = sub.plot([], [], '-', color='#FF330033', linewidth=1)
robot, = sub.plot([], [], '-', color='#FF330099', linewidth=2)

# Connect to network and start to redresh data.
net = network.Net(timer=REFRESH)
robot_x, robot_y = [0] * len(ROBOT), [0] * len(ROBOT)
way_x,   way_y   = [], []
objs_x,  objs_y  = [], []

# Update plots in infinit loop.
while net.receive():
    
    # Update plots on timer.
    if net.id == 'Timer':
        fig.canvas.draw()
        fig.canvas.flush_events()

    # Save robot coordinates.
    elif net.id == 'Coord':
        # Read coordinartes.
        pos     = net.msg.pos
        pos_x   = pos[X  ] if mat.is_num(pos[X  ]) else 0.0
        pos_y   = pos[Y  ] if mat.is_num(pos[Y  ]) else 0.0
        pos_yaw = pos[YAW] if mat.is_num(pos[YAW]) else 0.0
        # Update robot position.
        for i in range(len(ROBOT)):
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

    # Save objects coordinates.
    elif net.id == 'FilteredObjects':
        data = net.msg.objs
        for i in data:
            objs_x = np.append(objs_x, data[i][X])
            objs_y = np.append(objs_y, data[i][Y])
        while len(objs_x) > 10: objs_x = objs_x[1:]
        while len(objs_y) > 10: objs_y = objs_y[1:]
        objs.set_xdata(objs_x)
        objs.set_ydata(objs_y)
