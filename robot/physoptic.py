import math
import serial
import setproctitle
import sys

import threading

from base import message, network
from base.message import YAW

import time

#################
# CONFIGURATION #
BAUDRATE = 115200
PACKAGE_FREQ = 1200  # Packages per second
PORT_NAME = '/dev/ttyUSB0'

EARTH_ROTATION = 2.6656648454566797e-05
SENSOR_ERROR = 1.588
#################


class DataLostException(Exception):
    pass


class PackageLostException(DataLostException):
    pass


class ByteLostException(DataLostException):
    pass


class DataUnit:
    rate: float
    counter: int
    extra: int

    def __init__(self, rate, counter, extra):
        self.rate = rate
        self.counter = counter
        self.extra = extra


class DataSet:
    average_rate: float
    course_change: float
    temperature: float
    voltage: float
    current: float
    diagnostics: float

    def __init__(self, units, temperature, voltage, current, diagnostics):
        self.units = units
        self.temperature = temperature
        self.voltage = voltage
        self.current = current
        self.diagnostics = diagnostics

        rate_sum = sum([unit.rate for unit in units])
        self.average_rate = rate_sum / len(units)
        self.course_change = rate_sum / PACKAGE_FREQ


class PhysopticSerial(serial.Serial):
    def get_data_bytes(self):
        # Wait for starting byte to appear
        starting_byte = self.read()
        while starting_byte != b'\xdd':
            starting_byte = self.read()

        data = bytearray(starting_byte)
        for i in range(7):
            byte = self.read()

            # If we get a starting byte before the end of the package, it means we lost a byte
            if byte == '\xdd':
                raise ByteLostException()

            data.extend(byte)

        return data

    @staticmethod
    def bytes_to_unit(data):
        rate = int.from_bytes((data[2], data[3], data[1]), byteorder='big', signed=True) * 5 / 2 ** 24 / math.pi * 180

        rate += EARTH_ROTATION

        rate *= SENSOR_ERROR

        counter = data[4]
        extra = data[5]
        return DataUnit(rate, counter, extra)

    def get_data_unit(self) -> DataUnit:
        return self.bytes_to_unit(self.get_data_bytes())


# Thread for pitch receiving
def get_init_robot_thread():
    global pos_yaw

    net = network.Net()
    while net.receive():
        if net.id == "InitRobot":
            lock.acquire()  # Acquire the lock
            pos_yaw = net.msg.pos[YAW]  # Modify the shared variable
            lock.release()  # Release the lock


# Thread for depth meter reading
def send_yaw_thread():
    global pos_yaw

    net = network.Net()
    with PhysopticSerial(port=PORT_NAME, baudrate=BAUDRATE) as ser:
        delta_pos_list = [0]
        acc_yaw_list = [0]
        vel_yaw_list = [0]

        last_time = 0
        while True:
            delta_pos_list = [delta_pos_list[-1]]  # We keep last element to calculate speed
            acc_yaw_list = [acc_yaw_list[-1]]
            vel_yaw_list = [vel_yaw_list[-1]]

            # results in 20 packages per second (one package is an average of 60 data units)
            for i in range(PACKAGE_FREQ // 20):
                try:
                    data_unit = ser.get_data_unit()

                    delta_pos_list.append(vel_yaw_list[-1] * (time.time() - last_time))

                    acc_yaw_list.append((vel_yaw_list[-1] - data_unit.rate) / (time.time() - last_time))

                    vel_yaw_list.append(data_unit.rate)

                    last_time = time.time()
                except ByteLostException:
                    delta_pos_list.append(delta_pos_list[-1])
                    acc_yaw_list.append(acc_yaw_list[-1])
                    vel_yaw_list.append(vel_yaw_list[-1])

                    print('Byte lost')  # TODO: handle error.

            delta_pos = sum(delta_pos_list)
            acc_yaw = sum(acc_yaw_list) / len(acc_yaw_list)
            vel_yaw = sum(vel_yaw_list) / len(vel_yaw_list)

            lock.acquire()
            pos_yaw += delta_pos
            lock.release()

            net.send(message.SensorRU(pos_yaw=pos_yaw, vel_yaw=vel_yaw, acc_yaw=acc_yaw))


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

pos_yaw = 0
lock = threading.Lock()

# Create and start the threads
yaw_receiver = threading.Thread(target=get_init_robot_thread)
yaw_sender = threading.Thread(target=send_yaw_thread)

yaw_receiver.start()
yaw_sender.start()
