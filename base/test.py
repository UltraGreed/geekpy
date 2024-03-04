import network
import message

net = network.Net()

while net.receive():
    print(net.id)
    print(type(net.msg))
