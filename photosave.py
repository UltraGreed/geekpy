from base import message, network


net = network.Net()
msg = message.PhotoSave(camera='Bottom', folder='321')

net.send(msg)