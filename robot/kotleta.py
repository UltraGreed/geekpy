import sys
import setproctitle
import math

import dronecan
from dronecan import uavcan

import numpy as np

from base import message, network

# Linear (1) & quadric (2) thrusters' spread by axis
#######            X,      Y,   DEPTH,    YAW,  PITCH,   ROLL
SPREAD1 = [[ -300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 0: bow_left
           [  300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 1: bow_right
           [  160.00,   0.00, -300.00,   0.00,  -1.00,   1.00],  # Thruster 2: middle_left
           [ -160.00,   0.00, -300.00,   0.00,  -1.00,  -1.00],  # Thruster 3: middle_right
           [ -280.00,  67.00,    0.00,   0.43,   0.00,  -0.00],  # Thruster 4: stern_left
           [  280.00,  67.00,    0.00,  -0.43,   0.00,   0.00]]  # Thruster 5: stern_right


class EngineConfiguration:

    _index: int = 0
    _min: int = 0
    _max: int = 8191
    _cutoff: float = 0.33
    _rotation_dir: int = 1

    def __init__(
        self,
        index: int = 0,
        min: int = 0,
        max: int = 8191,
        cutoff: float = 0.33,
        rotation_dir: int = 1,
    ):
        if index >= 0 and index < 16:
            self._index = index
        else:
            raise ValueError

        if min >= 0 and min < max:
            self._min = min
        else:
            raise ValueError

        if max <= 8191 and max > min:
            self._max = max
        else:
            raise ValueError

        if cutoff >= 0 and cutoff <= 1:
            self._cutoff = cutoff
        else:
            raise ValueError

        if rotation_dir == 1 or rotation_dir == -1:
            self._rotation_dir = rotation_dir
        else:
            raise ValueError

    @property
    def index(self) -> int:
        return self._index

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    @property
    def cutoff(self) -> float:
        return self._cutoff

    @property
    def rotation_dir(self) -> float:
        return self._rotation_dir

    def get_raw_command(self, percents: float) -> int:
        input: int = int(abs(percents) / 100 * self.max)

        if input > 8191:
            input = 8191

        if input < self.min * self.cutoff:
            return 0

        input *= int(math.copysign(1, percents)) * self._rotation_dir

        return input


def sing(x: int) -> int:
    if x > 0:
        return 1
    elif x < 0:
        return -1

    return 0


class EngineConfigurationRevFix:

    _index: int = 0
    _min: int = 0
    _max: int = 8191
    _cutoff: float = 0.33
    _rotation_dir: int = 1
    _last_input: int = 0

    def __init__(
        self,
        index: int = 0,
        min: int = 0,
        max: int = 8191,
        cutoff: float = 0.33,
        rotation_dir: int = 1,
    ):
        if index >= 0 and index < 16:
            self._index = index
        else:
            raise ValueError

        if min >= 0 and min < max:
            self._min = min
        else:
            raise ValueError

        if max <= 8191 and max > min:
            self._max = max
        else:
            raise ValueError

        if cutoff >= 0 and cutoff <= 1:
            self._cutoff = cutoff
        else:
            raise ValueError

        if rotation_dir == 1 or rotation_dir == -1:
            self._rotation_dir = rotation_dir
        else:
            raise ValueError

    @property
    def index(self) -> int:
        return self._index

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    @property
    def cutoff(self) -> float:
        return self._cutoff

    @property
    def rotation_dir(self) -> float:
        return self._rotation_dir

    def get_raw_command(self, percents: float) -> int:
        input: int = int(abs(percents) / 100 * self.max)

        if input > 8191:
            input = 8191

        if input < self.min * self.cutoff:
            return 0

        input *= int(math.copysign(1, percents))

        result = input
        if sing(input) != sing(self._last_input):
            result = self._last_input

        self._last_input = input

        result *= self._rotation_dir
        
        return result


# in case of returning random input
# def send_raw_command(node, power):
#     cmd = [ 0, 0, 0, 0, 0, 0]
#     rotation_params = [ 1, -1, -1, 1, -1, 1 ]
#
#     for i in range(len(cmd)):
#         sign = int(math.copysign(1, power[i]))
#         current_power = round(abs(power[i]) / 100 * _MAX_POWER)
#
#         if current_power > 8191:
#             current_power = 8191 
#
#         cmd[i] = current_power * rotation_params[i] * sign
#
#         if abs(cmd[i]) < _MIN_POWER and power / (_MIN_POWER / _MAX_POWER) < random.random():
#             cmd[i] = 0
#
#     node.broadcast(uavcan.equipment.esc.RawCommand(cmd=cmd))


def send_raw_command(node, engines, power):
    cmd = []
    for i in range(0, len(engines)):
        cmd.append(engines[i].get_raw_command(power[i]))

    node.broadcast(uavcan.equipment.esc.RawCommand(cmd=cmd))


def matrixing(speed):
    return (np.array(SPREAD1) @ np.array(speed)).tolist()


def main():
    setproctitle.setproctitle(' '.join(sys.argv)) 

    net = network.Net()
    power = message.Control()

    node = dronecan.make_node("can0", node_id=100, bitrate=500000)

    use_rev_fix = False

    engine_conf = EngineConfiguration
    if use_rev_fix:
        engine_conf = EngineConfigurationRevFix

    engines = []
    engines.append(engine_conf(index=0, min=250, max=7000, rotation_dir=1))
    engines.append(engine_conf(index=1, min=250, max=7000, rotation_dir=-1))
    engines.append(engine_conf(index=2, min=250, max=7000, rotation_dir=-1))
    engines.append(engine_conf(index=3, min=250, max=7000, rotation_dir=1))
    engines.append(engine_conf(index=4, min=300, max=7000, rotation_dir=-1))
    engines.append(engine_conf(index=5, min=300, max=7000, rotation_dir=1))

    while net.receive():

        if net.id == "Control":
            power.power = net.msg.power
            send_raw_command(node, engines, power.power)

        if net.id == "Coord":
            power.power = matrixing(net.msg.speed)
            send_raw_command(node, engines, power.power)

    node.close()


if __name__ == '__main__':
    main()
