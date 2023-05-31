#!/usr/bin/python

import time

from net_lib import net
import msg

exam = msg.ExampleMessage("My hello world!")
net = net.Net()
i = 0
while True:
    i += 1
    exam.str += "."
    net.set(exam)
    print(exam.str)
    time.sleep(1)
