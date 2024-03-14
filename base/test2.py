import sys
sys.path.append("./")
from base import network
from base import message
import time

net = network.Net(set_ports=[32000], serialization_type="json")
msg = message.TestMessage(text="POSOS")

while True:
    net.send(msg)
    time.sleep(1)
