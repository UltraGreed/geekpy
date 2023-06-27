#!python3 test_receive.py
from base import network, message

net = network.Net(timer=3)
i, j = 0, 0

# Wait for messages or timer
while net.receive():
    if net.id == 'Timer':
        print(i, "Got timer:", net.id, net.msg)
        i += 1

    elif net.id == 'TestMessage':
        test_message = net.msg
        print(j, "Got message:", test_message.id, test_message.text)
        j += 1
