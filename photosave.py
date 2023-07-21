from base import message, network


net = network.Net()
msg = message.PhotoSave(camera='Bottom', folder='bw_test')

net.send(msg)