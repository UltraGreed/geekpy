import time

import serial
import setproctitle
import sys

from base import message, network


#########
# CONFIG
# EXP COEFS
alpha_coef = 0.7
beta_coef = 1 - alpha_coef


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


setproctitle.setproctitle(' '.join(sys.argv))  # Set filename.py title for process.
port_name = '/dev/ttyTHS1'
baudrate = 115200


def main():
    net = network.Net(timer=1)  # TODO: msg?

    average_depth = 0
    last_time = 0
    is_first = True
    vel_depth = 0

    with DepthMeterSerial(port=port_name, baudrate=baudrate) as ser:
        while True:
            try:
                unit = ser.get_data_unit()
                if is_first:
                    vel_depth = (average_depth * beta_coef + unit.depth * alpha_coef - average_depth) / (time.time() - last_time)
                    average_depth = average_depth * beta_coef + unit.depth * alpha_coef
                    last_time = time.time()
            except ByteLostException:
                print('BYTE WAS LOST')
            finally:
                net.send(message.Sensor(pos_depth=average_depth, vel_depth=vel_depth))


if __name__ == '__main__':
    main()
