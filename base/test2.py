import network
import message
import time

net = network.Net(serialization_type="json")
msg = message.TestMessage(text="POSOS")

while True:
    net.send(msg)
    time.sleep(1)
