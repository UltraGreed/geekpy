#!/usr/bin/python

import time

from base import net
import msg

exam = msg.ExampleMessage()
net = net.Net(timer=2)
i = 0
while True:
    i = i + 1
    got = net.get()

    if got == 'Timer':
        print(i, "Timer")
        continue

    if got.id == exam.id:
        exam = got
        print(i, exam.string)
        continue

    time.sleep(1)
