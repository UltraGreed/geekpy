#!python3
import setproctitle
import sys
import time

from base import network, message, mat
from base.message import X, Y, YAW

TIMER   = 0.05        # Integration and publication timer period.
MX, MY  = 1.50, 1.00  # Mass in lateral and longitudinal directions.
TIMEOUT = 0.5         # Force timeout.

setproctitle.setproctitle(' '.join(sys.argv))                        # Set filename.py title for process.
net    = network.Net(timer=TIMER)                                    # Network communication with timer event.
sensor = message.Sensor(pos_x=0.0, pos_y=0.0, vel_x=0.0, vel_y=0.0)  # Initial robot position and velocity.
raw    = message.OdometryRaw()                                       # Self raw data.

speed           = [0.0, 0.0]  # Last known Motion.speed data.
speed_time      = 0.0         # Time of Motion.speed refreshing.
yaw             = 0.0         # Last known robot yaw position.
integrator_time = time.time() # Last integration time.

# Wait for messages and timer ticks.
while net.receive():

    if net.id == 'Timer':                                                # If timesr has come:
        now = time.time()                                                # Measuring
        dt = now - integrator_time                                       # real
        integrator_time = now                                            # timeout.
        if (time.time() - speed_time) > TIMEOUT:                         # If motion speed old
            speed = [0.0, 0.0]                                           # then stop.
        raw.acc_x           = (speed[X] - sensor.vel[X]) / MX            # Calculate new acceleration
        raw.acc_y           = (speed[Y] - sensor.vel[Y]) / MY            # in X and Y axis.
        acc_west, acc_north = mat.rotate2map(raw.acc_x, raw.acc_y, yaw)  # Rotate acceleration to map.
        raw.vel_west       += dt * acc_west                              # Calculate new
        raw.vel_north      += dt * acc_north                             # velocity.
        sensor.pos[X]      += dt * raw.vel_west                          # Update position
        sensor.pos[Y]      += dt * raw.vel_north                         # and velocity in message.
        sensor.vel[X], sensor.vel[Y] = mat.rotate2robot(raw.vel_west, raw.vel_north, yaw)
        net.send(sensor)                                                 # Send sensor data to consumers
        net.send(raw)                                                    # and raw data to charts.

    elif net.id == 'Coord':     # If robot cordinates obtained
        yaw = net.msg.pos[YAW]  # then save robot yaw.
        speed      = net.msg.speed  # then save speed vector
        speed_time = time.time()    # and current time.
