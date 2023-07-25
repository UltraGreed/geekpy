import sys

import setproctitle

from base import message, network, timer


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
        open("/sys/class/gpio/gpio%d/direction" % gpio, "wt").write("%s\n" % direction)
    
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


def main(name, port):
    setproctitle.setproctitle(' '.join(sys.argv))

    GPIO.setup(port, GPIO.OUT)
    GPIO.output(port, GPIO.LOW)

    net = network.Net()
    time = timer.Timer(0)
    is_time = False
    while net.receive():
        if net.id == 'KeyOn' and net.msg.key == name:
            if net.msg.time != -1:
                is_time = True
                time = timer.Timer(net.msg.time)

            GPIO.output(port, GPIO.HIGH)

        if net.id == 'KeyOff' and net.msg.key == name or time.is_unlock and is_time:
            if is_time:
                is_time = False

            GPIO.output(port, GPIO.LOW)

    GPIO.unexport(port)


if __name__ == '__main__':
    name = sys.argv[1]
    port = sys.argv[2]

    main(name, port)
