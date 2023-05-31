import json

########################
###### NAVIGATION ######
########################

# Robot horizontal position, velocity and acceleration
class XY():
	def __init__(my, pos = [0.0, 0.0], vel = [0.0, 0.0], acc = [0.0, 0.0]):
		# my.id = type(my).__name__
		my.id = my.__class__.__name__
		my.pos_x, my.pos_y = pos[0], pos[1]
		my.vel_x, my.vel_y = pos[0], pos[1]
		my.acc_x, my.acc_y = pos[0], pos[1]
	def __str__(my):
		return json.dumps(my.__dict__)

# Robot up position, velocity (rate) and acceleration
class Up():
	def __init__(my, pos = 0.0, vel = 0.0, acc = 0.0):
		my.id = my.__class__.__name__
		my.pos, my.vel, my.acc = pos, vel, acc
	def __str__(my):
		return json.dumps(my.__dict__)

# Robot yaw position, velocity (rate) and acceleration
class Yaw():
	def __init__(my, pos = 0.0, vel = 0.0, acc = 0.0):
		my.id = my.__class__.__name__
		my.pos, my.vel, my.acc = pos, vel, acc
	def __str__(my):
		return json.dumps(my.__dict__)

# Robot incline (trim and roll angles) position, velocity and acceleration
class Incline():
	def __init__(my, pos = [0.0, 0.0], vel = [0.0, 0.0], acc = [0.0, 0.0]):
		my.id = my.__class__.__name__
		my.pos_trim, my.pos_roll = pos[0], pos[1]
		my.vel_trim, my.vel_roll = vel[0], vel[1]
		my.acc_trim, my.acc_roll = acc[0], acc[1]
	def __str__(my):
		return json.dumps(my.__dict__)

# Robot linear accelerations
class Acc():
	def __init__(my, x = 0.0, y = 0.0, up = 0.0):
		my.id = my.__class__.__name__
		my.x, my.y, my.up = x, y, up
	def __str__(my):
		return json.dumps(my.__dict__)

#####################
###### CONTROL ######
#####################

# Speed vector to electronic speed controller
class Speed():
	def __init__(my, x=0.0, y=0.0, up=0.0, yaw=0.0):
		my.id = my.__class__.__name__
		my.x, my.y, my.up, my.yaw = x, y, up, yaw
	def __str__(my):
		return json.dumps(my.__dict__)

# Switch on
class Key():
	def __init__(my, key='', time=1.0):
		my.id = my.__class__.__name__
		my.key  = key
		my.time = time
	def __str__(my):
		return json.dumps(my.__dict__)

# Start saving photo images
class PhotoOn():
	def __init__(my, time=10, period=0.5):
		my.id = my.__class__.__name__
		my.time   = time
		my.period = perid
	def __str__(my):
		return json.dumps(my.__dict__)

# Stop saving photo images
class PhotoOff():
	def __init__(my):
		my.id = my.__class__.__name__
	def __str__(my):
		return json.dumps(my.__dict__)

#####################################
###### AUV & OBJECTS POSITIONS ######
#####################################

# Auv, start point & object initial position
class IniAuv():
	def __init__(my, x=0.0, y=0.0, up=0.0, yaw=0.0):
		my.id = my.__class__.__name__
		my.x, my.y, my.up, my.yaw = x, y, up, yaw
	def __str__(my):
		return json.dumps(my.__dict__)

class IniObject():
	def __init__(my, obj='', x=None, y=None, up=None, yaw=None):
		my.id = my.__class__.__name__
		my.obj, my.x, my.y, my.up, my.yaw = obj, x, y, up, yaw
	def __str__(my):
		return json.dumps(my.__dict__)

# Recognized object
class Object():
	def __init__(my, obj='', x=0.0, y=0.0, up=0.0):
		my.id = my.__class__.__name__
		my.obj, my.x, my.y, my.up, my.yaw = obj, x, y, up
	def __str__(my):
		return json.dumps(my.__dict__)

# Filtered objects
class Objects():
	def __init__(my, objs=[]):
		my.id = my.__class__.__name__
		my.objs = objs
	def __str__(my):
		return json.dumps(my.__dict__)

# Ping delays of received signals
class Ping():
	def __init__(my, f=0.0, dt=[0.0, 0.0, 0.0, 0.0]):
		my.id = my.__class__.__name__
		my.dt = dt
	def __str__(my):
		return json.dumps(my.__dict__)

#####################
###### LOGGING ######
#####################

# Send text to blackbox and plot
class Text():
	def __init__(my, str=""):
		my.id = my.__class__.__name__
		my.str = str
	def __str__(my):
		return json.dumps(my.__dict__)

# Start logging data
class LogOn():
	def __init__(my, decim=0.5):
		my.id = my.__class__.__name__
		my.decim = decim
	def __str__(my):
		return json.dumps(my.__dict__)

# Stop logging data
class LogOff():
	def __init__(my):
		my.id = my.__class__.__name__
	def __str__(my):
		return json.dumps(my.__dict__)

# Show logged data to some port
class LogShow():
	def __init__(my, port=32000):
		my.id = my.__class__.__name__
		my.port = port
	def __str__(my):
		return json.dumps(my.__dict__)
