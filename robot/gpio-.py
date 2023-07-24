import sys

import setproctitle
import gpio4.GPIO as GPIO

from base import message, network


def main(name, port):
    setproctitle.setproctitle(' '.join(sys.argv))

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(port, GPIO.OUT)

    net = network.Net()
    while net.receive():
        if net.id == 'KeyOn':
            GPIO.output(port, GPIO.HIGH)

        if net.id == 'KeyOff':
            GPIO.output(port, GPIO.LOW)

    GPIO.cleanup(port)


if __name__ == '__main__':
    name = sys.argv[1]
    port = sys.argv[2]

    main(name, port)
