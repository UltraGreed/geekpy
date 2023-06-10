#!python3 map.py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time, sys
sys.path.append('../base')
import mat, network, message
from message import X, Y, YAW

XLIM, YLIM = [-12.5, 12.5], [ -5.0,  5.0]  # Plot axis limits
REFRESH    = 0.5                           # Refresh time, sec

pos_x, pos_y, pos_yaw = 0.0, 0.0, 0.0
net = network.Net(timer=REFRESH)

# matplotlib.use('TkAgg')
auv_b_x, auv_b_y = [], []
auv_p_x, auv_p_y = [], []
auv_t_x, auv_t_y = [], []

plt.ion()
fig = plt.figure()
fad = fig.add_subplot(1,1,1)
plt.xlim(XLIM)
plt.ylim(YLIM)

auv_b, = fad.plot(auv_b_x, auv_b_y, 'o',  linestyle=':', markersize=10, color='#66FF66', alpha=0.6)
auv_p, = fad.plot(auv_p_x, auv_p_y, 'g-', linewidth=3, color='#33DD33', alpha=0.4)
auv_t, = fad.plot(auv_t_x, auv_t_y, 'g-', linewidth=1, color='#009900', alpha=0.2)

# Update plots in infinit loop
while net.receive():
	
	if net.id() == 'Timer':
		# Update position
		auv_b.set_xdata(pos_x)
		auv_b.set_ydata(pos_y)
		auv_p.set_xdata([pos_x, pos_x + mat.sind(pos_yaw)])
		auv_p.set_ydata([pos_y, pos_y + mat.cosd(pos_yaw)])
		# Update trajectory
		auv_t_x = np.append(auv_t_x, pos_x)
		auv_t_y = np.append(auv_t_y, pos_y)
		auv_t.set_xdata(auv_t_x)
		auv_t.set_ydata(auv_t_y)
		# Update plot
		fig.canvas.draw()
		fig.canvas.flush_events()

	elif net.id() == 'Coord':
		pos     = net.msg().pos
		pos_x   = pos[X  ] if mat.is_num(pos[X  ]) else 0.0
		pos_y   = pos[Y  ] if mat.is_num(pos[Y  ]) else 0.0
		pos_yaw = pos[YAW] if mat.is_num(pos[YAW]) else 0.0
