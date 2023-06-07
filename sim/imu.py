import time

from base import net, msg

TIMEOUT = 1.0  # Force timeout
DT = 0.05  # Integration period
M = 0.1  # Mass in yaw axis

update_t = 0.0
ini = msg.IniAuv()  # -> ini_id = msg.IniAuv.id
speed = msg.Speed()  # ...
yaw = msg.Yaw()  # ...
xy = msg.XY()
net = net.Net(timer=DT, msg=[ini.id, speed.id])

while True:
    got = net.get()

    if got == 'Timer':
        if (time.time() - update_t) > TIMEOUT:
            speed = msg.Speed()

        xy.acc_x = DT * (speed.x - xy.vel_x) / M
        xy.acc_y = DT * (speed.y - xy.vel_y) / M
        xy.vel_x += DT * xy.acc_x
        xy.vel_y += DT * xy.acc_y
        xy.pos_x += DT * xy.vel_x
        xy.pos_y += DT * xy.vel_y

        yaw.acc = DT * (speed.yaw - yaw.vel) / M
        yaw.vel += DT * yaw.acc
        yaw.pos += DT * yaw.vel

        net.set(xy)
        net.set(yaw)

    elif got.id == ini.id:
        ini = got

        yaw = msg.Yaw(
            pos=ini.yaw
        )

        xy = msg.XY(
            pos=(ini.x, ini.y)
        )

    elif got.id == speed.id:
        speed = got
        update_t = time.time()
