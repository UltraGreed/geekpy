import time

from net_lib import net, msg

TIMEOUT = 1.0  # Force timeout
DT = 0.05  # Integration period
M = 0.1  # Mass in yaw axis

update_t = 0.0
ini = msg.IniAuv()
speed = msg.Speed()
yaw = msg.Yaw()
net = net.Net(timer=DT, msg=[ini.id, speed.id])

while True:
    got = net.get()

    if got == 'Timer':
        if (time.time() - update_t) > TIMEOUT:
            speed = msg.Speed()
        yaw.acc = DT * (speed.yaw - yaw.vel) / M
        yaw.vel += DT * yaw.acc
        yaw.pos += DT * yaw.vel
        net.set(yaw)

    elif got.id == ini.id:
        ini = got
        speed = msg.Speed()
        yaw = msg.Yaw()
        yaw.pos = ini.yaw

    elif got.id == speed.id:
        speed = got
        update_t = time.time()
