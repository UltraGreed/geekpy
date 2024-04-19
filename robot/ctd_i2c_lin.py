import threading

import setproctitle
import sys

from base import message, network
from base import ms5837
from base.message import PITCH
from base.mat import sind, calc_lin_approx

import time


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

####################################
# CONFIG                           #
# LEVER ARM FOR PITCH COMPENSATION #
LEVER_ARM = 0.3

#     SAMPLES FOR APPROXIMATION    #
SAMPLES_N = 5

#     FINAL SENSOR ADJUSTMENTS     #
OFFSET = 0
COEFFICIENT = 1
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

    depth_data = [set(), set()]

    last_time = 0
    approx_vel = 0

    net = network.Net()
    while True:
        if sensor.read():
            lock.acquire()  # Acquire the lock
            pitch_offset = LEVER_ARM * sind(pos_pitch)
            lock.release()  # Release the lock

            depth = sensor.depth() * COEFFICIENT + OFFSET - pitch_offset

            depth_data[0].add(time.time())
            depth_data[1].add(depth)

            # Calculate linear approximation and send corresponding message
            if len(depth_data) == SAMPLES_N:
                a, b = calc_lin_approx(depth_data)
                depth_data.clear()

                # Calculate metrics from approximation
                approx_depth = a * time.time() + b

                last_vel = approx_vel
                approx_vel = a

                approx_acc = (approx_vel - last_vel) / (time.time() - last_time)

                last_time = time.time()

                net.send(message.Sensor(pos_depth=approx_depth, vel_depth=approx_vel, acc_depth=approx_acc))
        else:
            print('Read error')
            exit(1)


pos_pitch = 0
lock = threading.Lock()

# Create and start the threads
pitch_receiver = threading.Thread(target=get_pitch_thread)
depth_sender = threading.Thread(target=send_depth_thread)

pitch_receiver.start()
depth_sender.start()
