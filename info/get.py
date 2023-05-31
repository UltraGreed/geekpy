#!/usr/bin/python
import time
import sys
sys.path.append('../all')
sys.path.append('../info')
import net
import msg

exam = msg.ExampleMessage()
net  = net.Net(timer=2, msg=[exam.id])
i    = 0
while True:

	i = i+1
	got = net.get()

	if got == 'Timer':
		print(i, "Timer")
		continue

	if got.id == exam.id:
		exam = got
		print(i, exam.str)
		continue
