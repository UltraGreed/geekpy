TIMEOUT = 1.0         # Force timeout
DT      = 0.05        # Integration period
MX, MY  = 15.0, 10.0  # Mass in lateral and longitudinal directions

import time
import math
import sys
sys.path.append('../all')
import deg
import net
import msg

update_t  = 0.0
vel_west  = 0.0
vel_north = 0.0
ini       = msg.IniAuv()
speed     = msg.Speed()
yaw       = msg.Yaw()
xy        = msg.XY()
net       = net.Net(timer=DT, msg=[ini.id, speed.id, yaw.id])

while True:

	got = net.get()

	if got == 'Timer':
		if (time.time() - update_t) > TIMEOUT:
			speed = msg.Speed()
		xy.acc_x   = (speed.x - xy.vel_x) / MX
		xy.acc_y   = (speed.y - xy.vel_y) / MY
		vel_west  += DT * ( xy.acc_x * deg.cos(yaw.pos) + xy.acc_y * deg.sin(yaw.pos))
		vel_north += DT * (-xy.acc_x * deg.sin(yaw.pos) + xy.acc_y * deg.cos(yaw.pos))
		xy.pos_x  += DT * vel_west
		xy.pos_y  += DT * vel_north
		xy.vel_x   = vel_west * deg.cos(yaw.pos) - vel_north * deg.sin(yaw.pos)
		xy.vel_y   = vel_west * deg.sin(yaw.pos) + vel_north * deg.cos(yaw.pos)
		net.set(xy)
		print(xy)

	elif got.id == ini.id:
		ini = got
		speed    = msg.Speed()
		xy       = msg.XY()
		yaw      = msg.Yaw()
		yaw.pos  = ini.yaw
		xy.pos_x = ini.x
		xy.pos_y = ini.y
		vel_x    = 0.0
		vel_y    = 0.0

	elif got.id == speed.id:
		speed    = got
		update_t = time.time()

	elif got.id == yaw.id:
		yaw = got
