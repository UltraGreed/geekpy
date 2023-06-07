#!/usr/bin/python

import time

from base import net
import msg

exam = msg.ExampleMessage("My hello world!")
net = net.Net()
i = 0
while True:
    i += 1
    exam.string += "."
    net.set(exam)
    print(exam.string)
    time.sleep(1)
