import sys
import time

import setproctitle

from base import message, network
from base.timer import Timer


class GPIOHandler:
    IN = 'in'
    OUT = 'out'

    HIGH = True
    LOW = False

    def __init__(self):
        self.gpio_fds = {}

    def export(self, gpio):
        open("/sys/class/gpio/export", "wt").write("%d\n" % gpio)

    def unexport(self, gpio):
        open("/sys/class/gpio/unexport", "wt").write("%d\n" % gpio)

    def setup(self, gpio, direction):
        self.export(gpio)
        while True:
            try:
                open("/sys/class/gpio/gpio%d/direction" % gpio, "wt").write("%s\n" % direction)
                break
            except:
                pass
    
    def _open(self, gpio):
        fd = open("/sys/class/gpio/gpio%d/value" % gpio, "r+")
        self.gpio_fds[gpio] = fd

    def _check_open(self, gpio):
        if gpio not in self.gpio_fds:
            self._open(gpio)

    def output(self, gpio, value):
        self._check_open(gpio)

        self.gpio_fds[gpio].seek(0)
        self.gpio_fds[gpio].write("1" if value else "0")
        self.gpio_fds[gpio].flush()

    def input(self, gpio):
        self._check_open(gpio)

        self.gpio_fds[gpio].seek(0)
        val = self.gpio_fds[gpio].read().strip()
        return False if val == "0" else True


GPIO = GPIOHandler()

GPIO_PORTS = [394, 396, 395, 392]
GPIO_MAP = {
            'Left'    : [GPIO_PORTS[0], False, Timer(0)],
            'Right'   : [GPIO_PORTS[1], False, Timer(0)],
            'Push'    : [GPIO_PORTS[2], False, Timer(0)],
            'Release' : [GPIO_PORTS[3], False, Timer(0)], 
           }


def main():
    setproctitle.setproctitle(' '.join(sys.argv))

    for it in GPIO_PORTS:
        GPIO.setup(it, GPIO.OUT)

    net = network.Net(0.05)
    while net.receive():
        if net.id == 'KeyOn' and GPIO_MAP.get(net.msg.key) != None:
            if net.msg.time != -1:
                GPIO_MAP[net.msg.key][1] = True
                GPIO_MAP[net.msg.key][2] = Timer(net.msg.time)

            GPIO.output(GPIO_MAP[net.msg.key][0], GPIO.HIGH)

        if net.id == 'KeyOff' and GPIO_MAP.get(net.msg.key) != None:
            GPIO_MAP[net.msg.key][1] = False
            GPIO.output(GPIO_MAP[net.msg.key][0], GPIO.LOW)

        for key in GPIO_MAP:
            if GPIO_MAP[key][1] and GPIO_MAP[key][2].is_unlock:
                GPIO_MAP[key][1] = False
                GPIO.output(GPIO_MAP[key][0], GPIO.LOW)

    for it in GPIO_PORTS:
        GPIO.unexport(it)


if __name__ == '__main__':
    main()
