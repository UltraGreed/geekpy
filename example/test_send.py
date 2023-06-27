#!python3
import time
from base import network, message

test_message = message.TestMessage()
net = network.Net()
i = 0

# Infinite loop of message sending
while True:

    i += 1
    test_message.text = "Text #" + str(i)
    net.send(test_message)
    print(time.time(), test_message.text)
    time.sleep(1)
