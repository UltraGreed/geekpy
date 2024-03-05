import network

net = network.Net(serialization_type="json")

while net.receive():
    print(net.id)
    print(type(net.msg))
