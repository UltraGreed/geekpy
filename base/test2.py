import network
import message
import time

net = network.Net()
msg = message.TestMessage(text="POSOS")

while True:
    net.send(msg)
    time.sleep(1)
