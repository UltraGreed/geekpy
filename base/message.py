import json

# Aliases of navigation vector elements (AXIS = size)
X, Y, DEPTH, YAW, PITCH, ROLL, AXIS = 0, 1, 2, 3, 4, 5, 6


# Parent class for all messages
class Message:
    @property
    def id(self):
        return self.__class__.__name__

    def __str__(self):
        return json.dumps(self.__dict__)


# Test message
class TestMessage(Message):
    def __init__(self, text="Hello world!"):
        self.text = text


# Test timer delays
class TestDelaySend(Message):
    def __init__(self, name="", num=0, time=0.0, text="TestDelaySend text."):
        self.name = name
        self.num = num
        self.time = time
        self.text = text


class TestDelayReply(Message):
    def __init__(self, name="", num=0, time=0.0, text="TestDelayReply text."):
        self.name = name
        self.num = num
        self.time = time
        self.text = text


########################
###### NAVIGATION ######
########################

# Input navigation sensor data
class Sensor(Message):
    def __init__(self, pos_x=None, pos_y=None, pos_depth=None, pos_yaw=None, pos_pitch=None, pos_roll=None,
                 vel_x=None, vel_y=None, vel_depth=None, vel_yaw=None, vel_pitch=None, vel_roll=None,
                 acc_x=None, acc_y=None, acc_depth=None, acc_yaw=None, acc_pitch=None, acc_roll=None):
        self.pos = [pos_x, pos_y, pos_depth, pos_yaw, pos_pitch, pos_roll]  # Vehicle position
        self.vel = [vel_x, vel_y, vel_depth, vel_yaw, vel_pitch, vel_roll]  # Vehicle velocity
        self.acc = [acc_x, acc_y, acc_depth, acc_yaw, acc_pitch, acc_roll]  # Vehicle acceleration


# Used navigation data
class Coord(Message):
    def __init__(self, pos_x=0.0, pos_y=0.0, pos_depth=0.0, pos_yaw=0.0, pos_pitch=0.0, pos_roll=0.0,
                 vel_x=0.0, vel_y=0.0, vel_depth=0.0, vel_yaw=0.0, vel_pitch=0.0, vel_roll=0.0,
                 acc_x=0.0, acc_y=0.0, acc_depth=0.0, acc_yaw=0.0, acc_pitch=0.0, acc_roll=0.0):
        self.pos = [pos_x, pos_y, pos_depth, pos_yaw, pos_pitch, pos_roll]  # Vehicle position
        self.vel = [vel_x, vel_y, vel_depth, vel_yaw, vel_pitch, vel_roll]  # Vehicle velocity
        self.acc = [acc_x, acc_y, acc_depth, acc_yaw, acc_pitch, acc_roll]  # Vehicle acceleration


############################
###### MOTION CONTROL ######
############################

# Tack command to regulator, speed or stabilization mode
class Tack(Message):
    def __init__(self, priority=0, time=1.0,
                 speed_x=None, speed_y=None, speed_depth=None, speed_yaw=None, speed_pitch=None, speed_roll=None,
                 stab_x=None, stab_y=None, stab_depth=None, stab_yaw=None, stab_pitch=None, stab_roll=None):
        self.priority = priority  # Priority of movement control: 0=Mission, 1=Keyboard, 2=Gamepad
        self.time = time  # Time of movement control
        self.speed = [speed_x, speed_y, speed_depth, speed_yaw, speed_pitch, speed_roll]  # Speed mode, m/s, deg/s
        self.stab = [stab_x, stab_y, stab_depth, stab_yaw, stab_pitch, stab_roll]  # Stabilization mode, m, deg


# Motion speed vector, m/s and deg/s (from regulator to spreader)
class Motion(Message):  # Motion speed, m/s, deg/s
    def __init__(self, x=0.0, y=0.0, depth=0.0, yaw=0.0, pitch=0.0, roll=0.0):
        self.speed = [x, y, depth, yaw, pitch, roll]


# Control vector of each truster power, % (from spreader to electronic speed controller)
class Control(Message):  # Thruster control power, %         #####
    def __init__(self, bow_left=0.0, bow_right=0.0,  # BL BR#
                 middle_left=0.0, middle_right=0.0,  # #
                 stern_left=0.0, stern_right=0.0):  # ML   MR #
        self.power = [bow_left, bow_right,  # ROBOT   #
                      middle_left, middle_right,  # SL     SR #
                      stern_left, stern_right]  ###########


#####################################
###### AUV & OBJECTS POSITIONS ######
#####################################

# Robot, start point & object initial position
class InitRobot(Message):
    def __init__(self, x=None, y=None, depth=None, yaw=None, pitch=None, roll=None):
        self.pos = [x, y, depth, yaw, pitch, roll]


class InitObject(Message):
    def __init__(self, obj='', x=None, y=None, up=None, yaw=None):
        self.obj = obj
        self.pos = [x, y, up, yaw]


class ResetObjects(Message):
    def __init__(self):
        pass


###############################
###### OBJECTS DETECTION ######
###############################

# Detection On
class DetectionOn(Message):
    def __init__(self, obj=''):
        self.obj = obj


# Detection Off
class DetectionOff(Message):
    def __init__(self, obj=''):
        self.obj = obj


# Detected object sended to scene
class DetectedObject(Message):
    def __init__(self, obj='', x=None, y=None, depth=None):
        self.obj = obj
        self.pos = [x, y, depth]


# Filtered objects sended from scene
class FilteredObjects(Message):
    def __init__(self, objs=None):
        if objs is None:
            objs = {
                "Zero": [0.0, 0.0, 0.0, 0.0],
                "BallR": [-5.0, 5.0, 2.0, -45.0],
                "BallY": [-6.0, 6.0, 2.0, -45.0],
                "BallG": [-7.0, 5.0, 2.0, -45.0],
                "CellB": [-10.0, 10.0, 2.0, 0.0],
                "CellY": [-10.0, 11.0, 2.0, 0.0],
                "CellR": [-10.0, 12.0, 2.0, 0.0],
                "Cells": [-9.5, 11.5, 2.0, 0.0],
                "Frame": [-3.0, 11.0, 2.0, 0.0],
            }
        self.objs = objs


###################################
###### IMAGE & PHOTO CONTROL ######
###################################

# Image link from saved object
class ImageLink(Message):
    def __init__(self, obj='', path="", file="", counter=0):
        self.obj = obj
        self.path = path
        self.file = file
        self.counter = counter


# Start saving photo images
class PhotoSave(Message):
    def __init__(self, camera='Bottom', folder="", time=10, period=0.2):
        self.camera = camera  # 'Bottom' or 'Front' camera
        self.folder = folder  # Folder name for saved images
        self.time = time  # Time of image saving
        self.period = period  # Imaging period


# Switch on photo camera
class PhotoOn(Message):
    def __init__(self, camera='Bottom', period=0.1):
        self.camera = camera  # 'Bottom' or 'Front' camera
        self.period = period  # Imaging period


# Switch off photo camera
class PhotoOff(Message):
    def __init__(self, camera='Bottom'):
        self.camera = camera  # 'Bottom' or 'Front' camera


######################################
###### ACOUSTIC & SOUND CONTROL ######
######################################

# Wave delay of received signals
class SoundDelay(Message):
    def __init__(self, freq=-1.0, left=-0.1, right=-0.1, back=-0.1, front=-0.1):
        self.freq = freq  # Signal frequency, Hz.
        self.dist = [left, right, back, front]  # Distance delay, m.


##########################
###### KEYS CONTROL ######
##########################

# Switch on GPIO key
class KeyOn(Message):
    def __init__(self, key='', time=3.0):
        self.key = key  # Turn on key of 'Grabber', 'BallLeft' or 'BallRight'
        self.time = time  # Time of hold the key, -1 = infinit


# Switch off GPIO key
class KeyOff(Message):
    def __init__(self, key=''):
        self.key = key  # Turn off key of 'Grabber', 'BallLeft' or 'BallRight'


#####################
###### LOGGING ######
#####################

"""

# Send text to blackbox and plot
class Text(Message):
    def __init__(self, str=""):
        self.str = str

# Start logging data
class LogOn(Message):
    def __init__(self, decim=0.5):
        self.decim = decim

# Stop logging data
class LogOff(Message):

# Show logged data to some port
class LogShow(Message):
    def __init__(self, port=32000):
        self.port = port

"""
