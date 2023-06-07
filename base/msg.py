import json


# TODO: Create base class for all messages

########################
###### NAVIGATION ######
########################

# Robot horizontal position, velocity and acceleration
class XY:
    def __init__(self, pos=(0.0, 0.0), vel=(0.0, 0.0), acc=(0.0, 0.0)):
        # self.id = type(self).__name__
        self.id = self.__class__.__name__
        self.pos_x, self.pos_y = pos[0], pos[1]
        self.vel_x, self.vel_y = vel[0], vel[1]
        self.acc_x, self.acc_y = acc[0], acc[1]

    def __str__(self):
        return json.dumps(self.__dict__)


# Robot up position, velocity (rate) and acceleration
class Depth:
    def __init__(self, pos=0.0, vel=0.0, acc=0.0):
        self.id = self.__class__.__name__
        self.pos, self.vel, self.acc = pos, vel, acc

    def __str__(self):
        return json.dumps(self.__dict__)


# Robot yaw position, velocity (rate) and acceleration
class Yaw:
    def __init__(self, pos=0.0, vel=0.0, acc=0.0):
        self.id = self.__class__.__name__
        self.pos, self.vel, self.acc = pos, vel, acc

    def __str__(self):
        return json.dumps(self.__dict__)


# Robot incline (trim and roll angles) position, velocity and acceleration
class Incline:
    def __init__(self, pos=(0.0, 0.0), vel=(0.0, 0.0), acc=(0.0, 0.0)):
        self.id = self.__class__.__name__
        self.pos_trim, self.pos_roll = pos[0], pos[1]
        self.vel_trim, self.vel_roll = vel[0], vel[1]
        self.acc_trim, self.acc_roll = acc[0], acc[1]

    def __str__(self):
        return json.dumps(self.__dict__)


# Robot linear accelerations
class Acc:
    def __init__(self, x=0.0, y=0.0, up=0.0):
        self.id = self.__class__.__name__
        self.x, self.y, self.up = x, y, up

    def __str__(self):
        return json.dumps(self.__dict__)


#####################
###### CONTROL ######
#####################

# Speed vector to electronic speed controller
class Speed:
    def __init__(self, x=0.0, y=0.0, up=0.0, yaw=0.0):
        self.id = self.__class__.__name__
        self.x, self.y, self.up, self.yaw = x, y, up, yaw

    def __str__(self):
        return json.dumps(self.__dict__)


# Switch on
class Key:
    def __init__(self, key='', time=1.0):
        self.id = self.__class__.__name__
        self.key = key
        self.time = time

    def __str__(self):
        return json.dumps(self.__dict__)


# Start saving photo images
class PhotoOn:
    def __init__(self, time=10, period=0.5):
        self.id = self.__class__.__name__
        self.time = time
        self.period = period

    def __str__(self):
        return json.dumps(self.__dict__)


# Stop saving photo images
class PhotoOff:
    def __init__(self):
        self.id = self.__class__.__name__

    def __str__(self):
        return json.dumps(self.__dict__)


#####################################
###### AUV & OBJECTS POSITIONS ######
#####################################

# Auv, start point & object initial position
class IniAuv:
    def __init__(self, x=0.0, y=0.0, up=0.0, yaw=0.0):
        self.id = self.__class__.__name__
        self.x, self.y, self.up, self.yaw = x, y, up, yaw

    def __str__(self):
        return json.dumps(self.__dict__)


class IniObject:
    def __init__(self, obj='', x=0, y=0, up=0, yaw=0):
        self.id = self.__class__.__name__
        self.obj, self.x, self.y, self.up, self.yaw = obj, x, y, up, yaw

    def __str__(self):
        return json.dumps(self.__dict__)


# Recognized object
class Object:
    def __init__(self, obj='', x=0.0, y=0.0, up=0.0, yaw=0.0):
        self.id = self.__class__.__name__
        self.obj, self.x, self.y, self.up, self.yaw = obj, x, y, up, yaw

    def __str__(self):
        return json.dumps(self.__dict__)


# Filtered objects
class Objects:
    def __init__(self, objs=None):
        if objs is None:
            objs = list()
        self.id = self.__class__.__name__
        self.objs = objs

    def __str__(self):
        return json.dumps(self.__dict__)


# Ping delays of received signals
class Ping:
    def __init__(self, f=0.0, dt=None):
        if dt is None:
            dt = [0.0, 0.0, 0.0, 0.0]
        self.id = self.__class__.__name__
        self.dt = dt

    def __str__(self):
        return json.dumps(self.__dict__)


#####################
###### LOGGING ######
#####################

# Send text to blackbox and plot
class Text:
    def __init__(self, string=""):
        self.id = self.__class__.__name__
        self.string = string

    def __str__(self):
        return json.dumps(self.__dict__)


# Start logging data
class LogOn:
    def __init__(self, decim=0.5):
        self.id = self.__class__.__name__
        self.decim = decim

    def __str__(self):
        return json.dumps(self.__dict__)


# Stop logging data
class LogOff:
    def __init__(self):
        self.id = self.__class__.__name__

    def __str__(self):
        return json.dumps(self.__dict__)


# Show logged data to some port
class LogShow:
    def __init__(self, port=32000):
        self.id = self.__class__.__name__
        self.port = port

    def __str__(self):
        return json.dumps(self.__dict__)
