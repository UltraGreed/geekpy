#!python3
import time, sys, setproctitle
import matplotlib
import matplotlib.pyplot as plt
# import matplotlib.artist as art
import numpy as np
sys.path.append('../base')
import mat, network, message
from message import X, Y, YAW

OBJECT_COLORS = {
    "Zero":  "#00000033",
    "BallR": "#EE000099",
    "BallY": "#EEEE0099",
    "BallG": "#00EE0099",
    "CellR": "#AA000099",
    "CellY": "#AAAA0099",
    "CellB": "#0000AA99",
    "Frame": "#FF00FF99",
}

# Max count of detected objects markers.
OBJ_COUNT = 600

# Static markers coordinates.
MARKERS = {
    # "Start":        ([0],
    #                  [0]),
    "Pool":         ([-13,   3, -13,   3],
                     [ -3,  -3,  14,  14]),
    "StartAndStab": ([ -2,   2,  -2,   2],
                     [ -2,  -2,   2,   2]),
    "Balls":        ([ -8,  -4,  -8,  -4],
                     [  4,   4,   7,   7]),
    "Bins":         ([-11,  -9, -11,  -9],
                     [  9,   9,  13,  13])

}

# Robot (X, Y) coordinates.
ROBOT = [( 0.0, -0.3),
         (-0.2, -0.4),
         ( 0.0,  0.4),
         ( 0.2, -0.4),
         ( 0.0, -0.3)]

REFRESH = 0.2       # Refresh time, sec.
POINTS  = 20 * 120  # Number of points in trajectories.

# matplotlib.use('TkAgg')
setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
plt.ion()
fig = plt.figure(num='Map')
sub = fig.add_subplot(1,1,1)
sub.axis('equal')

# Init robot position&trajectory and static markers.
for m in MARKERS:
    sub.plot(MARKERS[m][X], MARKERS[m][Y], '+', color='#00000066')
obj,   = sub.plot([], [], '.', color='#0066FF22')
objs,  = sub.plot([], [], 'o', color='#00000033') #color='#00FF6644')
way,   = sub.plot([], [], '-', color='#FF330066', linewidth=1)
robot, = sub.plot([], [], '-', color='#FF330099', linewidth=2)

# Connect to network and start to redresh data.
net = network.Net(timer=REFRESH)
robot_x, robot_y = [0] * len(ROBOT), [0] * len(ROBOT)
way_x,   way_y   = [], []
objs_x,  objs_y  = [], []
obj_x,   obj_y   = [], []

# Update plots in infinit loop.
while net.receive():
    
    # Update plots on timer.
    if net.id() == 'Timer':
        fig.canvas.draw()
        fig.canvas.flush_events()

    # Save robot coordinates.
    elif net.id() == 'Coord':
        # Read coordinartes.
        pos     = net.msg().pos
        pos_x   = pos[X  ] if mat.is_num(pos[X  ]) else 0.0
        pos_y   = pos[Y  ] if mat.is_num(pos[Y  ]) else 0.0
        pos_yaw = pos[YAW] if mat.is_num(pos[YAW]) else 0.0
        # Update robot position.
        for i in range(len(ROBOT)):
            dx, dy = mat.rotate2map(ROBOT[i][X], ROBOT[i][Y], pos_yaw)
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

    # Show filtered objects coordinates.
    elif net.id() == 'FilteredObjects':
        data = net.msg().objs
        objs_x = []
        objs_y = []
        for txt in sub.texts:
            txt.remove()
        for i in data:
            objs_x = np.append(objs_x, data[i][X])
            objs_y = np.append(objs_y, data[i][Y])
            color = OBJECT_COLORS[i] if i in OBJECT_COLORS else '#000000AA'
            # color = '#000000AA'
            # if i in OBJECT_COLORS:
            #     color = OBJECT_COLORS[i]
            # else:
            #     color = '#000000AA'
            sub.text(data[i][X], data[i][Y], i, color=color, fontsize='small')
        objs.set_xdata(objs_x)
        objs.set_ydata(objs_y)

    # Show detected object coordinates.
    elif net.id() == 'DetectedObject':
        data  = net.msg().pos
        obj_x = np.append(obj_x, data[X])
        obj_y = np.append(obj_y, data[Y])
        while len(obj_x) > OBJ_COUNT: obj_x = obj_x[1:]
        while len(obj_y) > OBJ_COUNT: obj_y = obj_y[1:]
        obj.set_xdata(obj_x)
        obj.set_ydata(obj_y)
