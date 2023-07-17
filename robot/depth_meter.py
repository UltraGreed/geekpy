import threading

import serial
import setproctitle
import sys
import time

from base import message, network
from base.message import PITCH
from base.mat import sind

#########
# CONFIG
# EXPONENTIAL AVERAGE COEFS
ALPHA_COEF = 0.7
BETA_COEF = 1 - ALPHA_COEF
# LEVER ARM FOR PITCH COMPENSATION
LEVER_ARM = 0.3
# SERIAL PORT CONFIGURATION
PORT_NAME = '/dev/ttyTHS1'
BAUDRATE = 115200


class DataLostException(Exception):
    pass


class PackageLostException(DataLostException):
    pass


class ByteLostException(DataLostException):
    pass


class DataUnit:
    temperature: float
    depth: float

    def __init__(self, temperature, depth):
        self.temperature = temperature
        self.depth = depth


class DepthMeterSerial(serial.Serial):
    def get_data_bytes(self):
        # Wait for starting byte to appear
        data = bytearray()

        byte = self.read()
        while byte != b'T':
            byte = self.read()

        data.extend(byte)

        # Read 2 points
        while data.count(b'.') < 2:
            byte = self.read()
            data.extend(byte)

        # Read 2 digits after second point
        for i in range(2):
            byte = self.read()
            data.extend(byte)

        # If we get a starting byte before the end of the package, it means we lost a byte
        if data.count(b'T') > 1:
            raise ByteLostException()

        return data

    @staticmethod
    def bytes_to_unit(data):
        temperature = float(data[2:data.find(b'D')])
        depth = float(data[data.find(b'D') + 2:])
        return DataUnit(temperature, depth)

    def get_data_unit(self) -> DataUnit:
        return self.bytes_to_unit(self.get_data_bytes())


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

    average_depth = 0
    last_time = 0
    vel_depth = 0

    net = network.Net()
    with DepthMeterSerial(port=PORT_NAME, baudrate=BAUDRATE) as ser:
        while True:
            try:
                unit = ser.get_data_unit()

                last_depth = average_depth

                lock.acquire()  # Acquire the lock
                pitch_offset = LEVER_ARM * sind(pos_pitch)
                lock.release()  # Release the lock

                # Calculate exponential average depth
                average_depth = average_depth * BETA_COEF + (unit.depth - pitch_offset) * ALPHA_COEF

                vel_depth = (average_depth - last_depth) / (time.time() - last_time)

                last_time = time.time()
            except ByteLostException:
                print('BYTE WAS LOST')
            finally:
                net.send(message.Sensor(pos_depth=average_depth, vel_depth=vel_depth))


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

pos_pitch = 0
lock = threading.Lock()

# Create and start the threads
pitch_receiver = threading.Thread(target=get_pitch_thread)
depth_sender = threading.Thread(target=send_depth_thread)

pitch_receiver.start()
depth_sender.start()
