import serial
import setproctitle
import sys

from base import message, network

import time

#################
# CONFIGURATION #
BAUDRATE = 115200
PACKAGE_FREQ = 1200  # Packages per second
PORT_NAME = '/dev/ttyUSB0'
EARTH_ROTATION = -0.0050437326344210075
# From datasheet
# SCALE_COEFFICIENT = 0.006  # For VG103PD
SCALE_COEFFICIENT = 0.012  # For VG103PD-200SH
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
        rate = int.from_bytes((data[2], data[3], data[1]), byteorder='big', signed=True) * 5 / 2**24
        rate /= SCALE_COEFFICIENT  

        counter = data[4]
        extra = data[5]
        return DataUnit(rate, counter, extra)

    def get_data_unit(self) -> DataUnit:
        return self.bytes_to_unit(self.get_data_bytes())


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.

pos_yaw = 0

# Depth meter reading
net = network.Net()
with PhysopticSerial(port=PORT_NAME, baudrate=BAUDRATE) as ser:
    is_connected = True
    vel_yaw_list = [0]

    last_time = time.time()
    while True:
        vel_yaw_list = [vel_yaw_list[-1]]

        # results in 20 packages per second (one package is an average of 60 data units)
        for i in range(PACKAGE_FREQ // 20):
            try:
                data_unit = ser.get_data_unit()

                vel_yaw_list.append(data_unit.rate)

            except ByteLostException:
                print('!\nPhysoptic byte lost\n!')  # TODO: handle error.
            except serial.serialutil.SerialException:
                print('!\nPhysoptica naebnulas\'!!!\n!')

                pos_yaw = 0

                ser.close()

                time.sleep(1)

                try:
                    ser.open()
                    print('Physoptica reconnected')
                except serial.serialutil.SerialException:
                    print('!\nPhysoptica reconnected failed!\n!')

        vel_yaw = sum(vel_yaw_list) / len(vel_yaw_list) - EARTH_ROTATION
        delta_pos = vel_yaw * (time.time() - last_time)

        last_time = time.time()

        pos_yaw = (pos_yaw + delta_pos + 180) % 360 - 180

        net.send(message.Sensor(pos_yaw=pos_yaw, vel_yaw=vel_yaw))
