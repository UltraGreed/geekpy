#!python3
import time, sys, setproctitle
sys.path.append('../base')
import network, message
name = ' '.join(sys.argv)
num  = int(sys.argv[1])

Hz = 100

setproctitle.setproctitle(name)  # Set filename.py title for process.
net = network.Net(timer=1.0/Hz)  # Network communication.

# Wait for messages or timer
cycle = 0
while net.receive():

    if net.id() == 'Timer':
        if cycle % Hz == 0:
            print("\n{:d}:{:.4f} ".format(cycle, time.time()), end=" ", flush=True)
        net.send(message.TestDelaySend(name=name, num=num, time=time.time(), text="TestDelaySend generated."))
        cycle += 1

    elif net.id() == 'TestDelaySend':
        msg = net.msg
        if msg.field_id == name:
            if cycle % Hz == 0:
                print("s={:d}:{:.4f}  ".format(msg.num, time.time() - msg.time), end=" ", flush=True)
        else:
            net.send(message.TestDelayReply(name=msg.field_id, num=num, time=msg.time, text="TestDelayReply generated."))

    elif net.id() == 'TestDelayReply':
        msg = net.msg
        if msg.field_id == name:
            if cycle % Hz == 0:
                print("r={:d}:{:.4f}  ".format(msg.num, time.time() - msg.time), end=" ", flush=True)
