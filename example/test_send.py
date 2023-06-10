#!python3 test_send.py
import time, sys
sys.path.append('../base')
import network, message

test_message = message.TestMessage()
net = network.Net()
i = 0

# Infinit loop of message sending
while True:

    i += 1
    test_message.text = "Text #" + str(i)
    net.send(test_message)
    print(test_message.text)
    time.sleep(1)
