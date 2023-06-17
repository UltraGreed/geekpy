#!python3 imu.py
import time, sys, setproctitle
sys.path.append('../base')
import network, message
from message import YAW

TIMEOUT = 0.50  # Force timeout.
PERIOD  = 0.05  # Integration period and publication timer.
MOMENT  = 0.02  # Momement of inertion in yaw axis.

setproctitle.setproctitle(sys.argv[0])  # Set filename.py title for process.
net    = network.Net(timer=PERIOD)      # Network communication.
sensor = message.Sensor()               # Sensor class for simulated message with yaw.

yaw_time        = 0.0  # Timestamp of incoming last control values 'Speed'.
yaw_speed       = 0.0  # Current yaw speed.
sensor.pos[YAW] = 0.0  # Redefine initial yaw position (None by default).
sensor.vel[YAW] = 0.0  # Redefine initial yaw velocity (None by default).
sensor.acc[YAW] = 0.0  # Redefine initial yaw accelerarion (None by default).

while net.receive():  # Wait for messages and ticks.

    if net.id() == 'Timer':                                                 # On timer:
        if time.time() - yaw_time > TIMEOUT:                                # If yaw data too old
            yaw_speed = 0.0                                                 # then make speed zero.
        sensor.acc[YAW]  = PERIOD * (yaw_speed - sensor.vel[YAW]) / MOMENT  # Calculate acceleration,
        sensor.vel[YAW] += PERIOD * sensor.acc[YAW]                         # velocity and
        sensor.pos[YAW] += PERIOD * sensor.vel[YAW]                         # position.
        net.send(sensor)                                                    # Send Sensor message.

    elif net.id() == 'Motion':            # If Motion message has come then
        yaw_speed = net.msg().speed[YAW]  # save yaw speed
        yaw_time  = time.time()           # and timestamp.
