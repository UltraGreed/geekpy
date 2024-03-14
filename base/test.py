import sys
sys.path.append("./")

from base import network

net = network.Net()

while net.receive():
    print(net.msg)
