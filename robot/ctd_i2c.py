import threading

import setproctitle
import sys

from base import message, network
from base import ms5837
from base.message import PITCH
from base.mat import sind

import time

####################################
# CONFIG                           #
# EXPONENTIAL AVERAGE COEFS        #
ALPHA_COEF = 0.7
BETA_COEF = 1 - ALPHA_COEF
# LEVER ARM FOR PITCH COMPENSATION #
LEVER_ARM = 0.3
####################################


# Thread for pitch receiving
def get_pitch_thread():
    global pos_pitch

    net = network.Net()
    while net.receive():
        if net.id == "Coord":
            lock.acquire()  # Acquire the lock
            pos_pitch = net.msg.pos[PITCH]  # Modify the shared variable
            lock.release()  # Release the lock


# Thread for depth meter reading
def send_depth_thread():
    global pos_pitch

    sensor = ms5837.MS5837_30BA()  # Default I2C bus is 1 (Raspberry Pi 3)

    # We must initialize the sensor before reading it
    if not sensor.init():
        print("Sensor could not be initialized")
        exit(1)

    # We have to read values from sensor to update pressure and temperature
    if not sensor.read():
        print("Sensor read failed!")
        exit(1)

    average_depth = 0
    last_time = 0
    vel_depth = 0

    net = network.Net()
    while True:
        if sensor.read():
            lock.acquire()  # Acquire the lock
            pitch_offset = LEVER_ARM * sind(pos_pitch)
            lock.release()  # Release the lock

            # Calculate exponential average depth
            last_depth = average_depth
            average_depth = average_depth * BETA_COEF + (sensor.depth() - pitch_offset) * ALPHA_COEF

            last_vel_depth = vel_depth
            vel_depth = (average_depth - last_depth) / (time.time() - last_time)

            acc_depth = (vel_depth - last_vel_depth) / (time.time() - last_time)

            last_time = time.time()

            net.send(message.Sensor(pos_depth=average_depth, vel_depth=vel_depth, acc_depth=acc_depth))
        else:
            print('Read error')
            exit(1)


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

pos_pitch = 0
lock = threading.Lock()

# Create and start the threads
pitch_receiver = threading.Thread(target=get_pitch_thread)
depth_sender = threading.Thread(target=send_depth_thread)

pitch_receiver.start()
depth_sender.start()
