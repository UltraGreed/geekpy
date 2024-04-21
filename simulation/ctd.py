import sys, time, setproctitle
from base import network, message
from base.message import DEPTH

TIMEOUT = 0.50  # Force timeout.
PERIOD  = 0.05  # Integration period and publication timer.
MOMENT  = 0.10  # Momement of inertion in yaw axis.

setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
net    = network.Net(timer=PERIOD)             # Network communication.
sensor = message.Sensor()                      # Sensor class for simulated message with yaw.

depth_time        = 0.0         # Timestamp of incoming last control values 'Speed'.
depth_speed       = 0.0         # Current yaw speed.
floating_speed    = -0.2
cur_depth = 0.0
buoyancy = 0.025
sensor.pos[DEPTH] = cur_depth         # Redefine initial yaw position (None by default).
sensor.vel[DEPTH] = 0.0         # Redefine initial yaw velocity (None by default).
sensor.acc[DEPTH] = 0.0         # Redefine initial yaw accelerarion (None by default).
integrator_time = time.time() # Last integration time.

# Wait for messages and ticks.
while net.receive():
    
    if net.id == 'Timer':                                               # On timer:
        now = time.time()                                               # Measuring
        dt = now - integrator_time                                      # real
        integrator_time = now                                           # timeout.
        if time.time() - depth_time > TIMEOUT:                            # If yaw data too old
            depth_speed = 0.0                                             # then make speed zero.

        volume = 1.0
        if cur_depth < 0.2:
            volume = cur_depth / 0.2

        sensor.acc[DEPTH]  = dt * (depth_speed - buoyancy * volume - sensor.vel[DEPTH]) / MOMENT  # Calculate acceleration,
        sensor.vel[DEPTH] += dt * sensor.acc[DEPTH]                         # velocity and
        sensor.pos[DEPTH] += dt * sensor.vel[DEPTH]                         # position.

        net.send(sensor)                                                # Send Sensor message.

    elif net.id == 'Coord':            # If Motion message has come then
        depth_speed = net.msg.spd[DEPTH]  # save yaw speed
        cur_depth = net.msg.pos[DEPTH]
        depth_time  = time.time()         # and timestamp.
