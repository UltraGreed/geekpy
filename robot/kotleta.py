import sys
import setproctitle
import math

import dronecan
from dronecan import uavcan

import numpy as np

from base import message as m, network

# Linear (1) & quadric (2) thrusters' spread by axis
#######            X,      Y,   DEPTH,    YAW,  PITCH,   ROLL
SPREAD1 = [[ -300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 0: bow_left
           [  300.00,   0.00, -250.00,   0.00,   1.00,   0.00],  # Thruster 1: bow_right
           [  160.00,   0.00, -300.00,   0.00,  -1.00,   1.00],  # Thruster 2: middle_left
           [ -160.00,   0.00, -300.00,   0.00,  -1.00,  -1.00],  # Thruster 3: middle_right
           [ -280.00,  67.00,    0.00,   0.43,   0.00,   0.00],  # Thruster 4: stern_left
           [  280.00,  67.00,    0.00,  -0.43,   0.00,   0.00]]  # Thruster 5: stern_right

#          i   min   max  coff rdir
CONF = [[  0,  250, 8191, 0.33,  1],
        [  1,  250, 8191, 0.33, -1],
        [  2,  250, 8191, 0.33, -1],
        [  3,  250, 8191, 0.33,  1],
        [  4,  300, 8191, 0.33, -1],
        [  5,  300, 8191, 0.33,  1]]

PRIORITY = [m.PITCH, m.ROLL, m.YAW, m.DEPTH, m.X, m.Y]


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


class EngineConfigurationAlarm:

    _index: int = 0
    _min: int = 0
    _max: int = 8191
    _cutoff: float = 0.33
    _rotation_dir: int = 1
    _last_input: int = 0
    _need_more: bool = False

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

        if self._need_more:
            result = self._last_input
            self._need_more = False
        elif sing(input) != sing(self._last_input):
            self._need_more = True

        self._last_input = input

        result *= self._rotation_dir
        
        return result


def send_raw_command(node, engines, power):
    cmd = []
    for i in range(0, len(engines)):
        cmd.append(engines[i].get_raw_command(power[i]))

    node.broadcast(uavcan.equipment.esc.RawCommand(cmd=cmd))


def matrixing(speed):
    return (np.array(SPREAD1) @ np.array(speed)).tolist()


def matrixing_prior(speed):
    pass


def main():
    setproctitle.setproctitle(' '.join(sys.argv)) 

    net = network.Net()

    node = dronecan.make_node("can0", node_id=100, bitrate=500000)

    use_rev_fix = False

    engine_conf = EngineConfiguration
    if use_rev_fix:
        engine_conf = EngineConfigurationAlarm

    engines = []
    for i in CONF:
        engines.append(
            engine_conf(index=i[0], min=i[1], max=i[2], cutoff=i[3], rotation_dir=i[4])
        )

    while net.receive():

        if net.id == "Control":
            power = net.msg.power
            send_raw_command(node, engines, power)

        if net.id == "Coord":
            power = matrixing(net.msg.speed)
            send_raw_command(node, engines, power)

    node.close()


if __name__ == '__main__':
    main()
