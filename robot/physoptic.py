import math

import serial

from base import msg, net


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
    units: list[DataUnit]
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
        self.course_change = rate_sum / package_freq


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
        rate = (2.5 * int.from_bytes((data[2], data[3], data[1]), byteorder='big', signed=True) / 2 ** 23 - earth_rotation) / math.pi * 180
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


read_interval = 0
port_name = '/dev/ttyUSB0'
baudrate = 115000
package_freq = 1200  # Packages per second
earth_rotation = 2.6656648454566797e-05


def main():
    init_id = msg.IniAuv().id

    network = net.Net()

    yaw = msg.Yaw()

    received = network.get()
    if received.id == init_id:
        yaw.pos = received.yaw
    print('Initial yaw received')

    with PhysopticSerial(port=port_name, baudrate=baudrate) as ser:
        # 18.75 times per second we send 1 UDP package, containing an average of 4 data sets or 64 packages
        while True:
            data_sets = [ser.get_data_set() for _ in range(4)]
            yaw.vel = sum(data_set.average_rate for data_set in data_sets) / 4
            yaw.pos += sum(data_set.course_change for data_set in data_sets)

            network.set(yaw)
            print(f'Course change: {yaw.vel}')
            print(f'Course: {yaw.pos}')


if __name__ == '__main__':
    main()
