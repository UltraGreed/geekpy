from base import network, message


power = 5
net = network.Net(timer=0.05)
while net.receive():
    if net.id == 'Timer':
        net.send(message.Control(
            *[power for _ in range(6)]
        ))