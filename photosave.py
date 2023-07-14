from base import message, network


net = network.Net()
msg = message.PhotoSave(camera='bottom', folder='123')

net.send(msg)