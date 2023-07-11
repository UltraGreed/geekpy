#!python3
import time, math, sys, setproctitle
sys.path.append('../base')
import mat, network, message
from mat import sind, cosd
from message import X, Y, YAW

TIMER   = 0.05        # Integration and publication timer period.
MX, MY  = 1.50, 1.00  # Mass in lateral and longitudinal directions.
TIMEOUT = 0.5         # Force timeout.

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net    = network.Net(timer=TIMER)              # Network communication with timer event.
sensor = message.Sensor(pos_x=0.0, pos_y=0.0,  # Initial robot position
                        vel_x=0.0, vel_y=0.0)  # and velocity.

speed               = [0.0, 0.0]  # Last known Motion.speed data.
speed_time          = 0.0         # Time of Motion.speed refreshing.
vel_west, vel_north = 0.0, 0.0    # Calculated robot velocity.
yaw                 = 0.0         # Last known robot yaw position.
integrator_time     = time.time() # Last integration time.

while net.receive():  # Wait for messages and timer ticks.

    if net.id == 'Timer':                                               # If timesr has come:
        now = time.time()                                               # Measuring
        dt = now - integrator_time                                      # real
        integrator_time = now                                           # timeout.
        if (time.time() - speed_time) > TIMEOUT:                        # If motion speed old
            speed = [0.0, 0.0]                                          # then stop.
        acc_x          = (speed[X] - sensor.vel[X]) / MX                # Calculate new acceleration
        acc_y          = (speed[Y] - sensor.vel[Y]) / MY                # in X and Y axis.
        vel_west      += dt * ( acc_x * cosd(yaw) + acc_y * sind(yaw))  # Calculate new
        vel_north     += dt * (-acc_x * sind(yaw) + acc_y * cosd(yaw))  # velocity.
        sensor.pos[X] += dt * vel_west                                  # Update position in
        sensor.pos[Y] += dt * vel_north                                 # outgoing message.
        sensor.vel[X]  = vel_west * cosd(yaw) - vel_north * sind(yaw)   # Update velocity in
        sensor.vel[Y]  = vel_west * sind(yaw) + vel_north * cosd(yaw)   # outgoing message.
        net.send(sensor)

    elif net.id == 'Motion':          # If Motion message has come
        speed      = net.msg().speed  # then save speed vector
        speed_time = time.time()      # and current time.

    elif net.id == 'Coord':       # If robot cordinates obtained
        yaw = net.msg().pos[YAW]  # then save robot yaw.
