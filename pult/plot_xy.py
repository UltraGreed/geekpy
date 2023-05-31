XLIM = [-12.5, 12.5]
YLIM = [ -5.0,  5.0]

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
sys.path.append('../all')
import deg
import net
import msg

xy   = msg.XY()
yaw  = msg.Yaw()
net  = net.Net(msg=[xy.id, yaw.id], timer=0.5)

matplotlib.use('TkAgg')
auv_b_x, auv_b_y = [], []
auv_p_x, auv_p_y = [], []
auv_t_x, auv_t_y = [], []

plt.ion()
fig    = plt.figure()
ax     = fig.add_subplot(1,1,1)
plt.xlim(XLIM)
plt.ylim(YLIM)

auv_b, = ax.plot(auv_b_x, auv_b_y, linestyle=':', marker='o', markersize=10, color='#66FF66', alpha=0.6)
auv_p, = ax.plot(auv_p_x, auv_p_y, 'g-', linewidth=3, color='#33DD33', alpha=0.4)
auv_t, = ax.plot(auv_t_x, auv_t_y, 'g-', linewidth=1, color='#009900', alpha=0.2)

# Update plots in infinit loop
while True:
	got = net.get()
	
	if got == 'Timer':
		# Update position
		auv_b.set_xdata([xy.pos_x])
		auv_b.set_ydata([xy.pos_y])
		auv_p.set_xdata([xy.pos_x, xy.pos_x + deg.sin(yaw.pos)])
		auv_p.set_ydata([xy.pos_y, xy.pos_y + deg.cos(yaw.pos)])
		# Update trajectory
		auv_t_x = np.append(auv_t_x, xy.pos_x)
		auv_t_y = np.append(auv_t_y, xy.pos_y)
		auv_t.set_xdata(auv_t_x)
		auv_t.set_ydata(auv_t_y)
		# Update plot
		fig.canvas.draw()
		fig.canvas.flush_events()

	elif got.id == xy.id:
		xy = got

	elif got.id == yaw.id:
		yaw = got
