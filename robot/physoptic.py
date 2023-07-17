import math
import serial
import setproctitle
import sys

import threading

from base import message, network
from base.message import YAW


BAUDRATE = 115200
PACKAGE_FREQ = 1200  # Packages per second


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

        if abs(rate) < sensor_error:
            rate = 0

        counter = data[4]
        extra = data[5]
        return DataUnit(rate, counter, extra)

    def get_data_unit(self) -> DataUnit:
        return self.bytes_to_unit(self.get_data_bytes())

    # Returns data set of 16 data units with all extra data
    def get_data_set(self):
        units = list()
        temperature_b = [255, 255]
        voltage_b = [255, 255]
        current_b = [255, 255]
        diagnostics_b = [255, 255]

        # Package loss check
        last_counter = -1
        was_lost = False
        while len(units) < 16:
            unit = self.get_data_unit()

            if units and (last_counter + 1) % 16 != unit.counter:
                # If we lost a package, we duplicate the last one
                units.append(units[0])
                was_lost = True
                # raise PackageLostException TODO: IDK if we will need an exception here

            units.append(unit)

            if unit.counter == 0:
                temperature_b[0] = unit.extra
            elif unit.counter == 1:
                temperature_b[1] = unit.extra
            elif unit.counter == 2:
                voltage_b[0] = unit.extra
            elif unit.counter == 3:
                voltage_b[1] = unit.extra
            elif unit.counter == 4:
                current_b[0] = unit.extra
            elif unit.counter == 5:
                current_b[1] = unit.extra
            elif unit.counter == 6:
                diagnostics_b[0] = unit.extra
            elif unit.counter == 7:
                diagnostics_b[1] = unit.extra

            last_counter = unit.counter

        # If a package was lost, we can not get extra data
        if was_lost:
            temperature = None
            voltage = None
            current = None
            diagnostics = None
        else:
            temperature = int.from_bytes(temperature_b, byteorder='big', signed=True) * 250 / 2 ** 15 - 50
            voltage = int.from_bytes(voltage_b, byteorder='big', signed=True) * 2.5 / 2 ** 15 / 0.25
            current = int.from_bytes(current_b, byteorder='big', signed=True) * 2.5 / 2 ** 15 / 10
            diagnostics = int.from_bytes(diagnostics_b, byteorder='big', signed=True) * 2.5 / 2 ** 15

        return DataSet(units, temperature, voltage, current, diagnostics)


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
def send_depth_thread():
    global pos_yaw

    net = network.Net()
    with PhysopticSerial(port=port_name, baudrate=BAUDRATE) as ser:
        # 75 times per second we send 1 UDP package, containing an average of 1 data set or 16 packages
        while True:
            try:
                data_sets = ser.get_data_set()

                vel_yaw = sum(data_set.average_rate for data_set in data_sets)

                lock.acquire()
                pos_yaw += sum(data_set.course_change for data_set in data_sets)
                lock.release()
            except ByteLostException:
                print('Byte lost')  # TODO: handle error.
            finally:
                net.send(message.Sensor(pos_yaw=pos_yaw, vel_yaw=vel_yaw))
                print(f'Course change: {vel_yaw}')
                print(f'Course: {pos_yaw}')


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
port_name = '/dev/ttyUSB0'
sensor_error = 2.6656648454566797e-05

pos_yaw = 0
lock = threading.Lock()

# Create and start the threads
yaw_receiver = threading.Thread(target=get_init_robot_thread)
yaw_sender = threading.Thread(target=send_depth_thread)

yaw_receiver.start()
yaw_sender.start()
