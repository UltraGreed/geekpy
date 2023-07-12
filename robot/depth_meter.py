import serial
import setproctitle
import sys

from base import message, network


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
read_interval = 0
port_name = '/dev/ttyTHS1'
baudrate = 115200
package_freq = 10  # Packages per second


def main():
    net = network.Net(timer=1)  # TODO: msg?

    pos_depth = 0
    is_first = True

    with DepthMeterSerial(port=port_name, baudrate=baudrate) as ser:
        while True:
            try:
                unit = ser.get_data_unit()
                if not is_first:
                    vel_depth = (unit.depth - pos_depth) / package_freq
                else:
                    vel_depth = 0
                    is_first = False
            except ByteLostException:
                pass
            finally:
                net.send(message.Sensor(pos_depth=unit.depth, vel_depth=vel_depth))


if __name__ == '__main__':
    main()
