import sys
import termios
import tty

from net_lib import net, msg


def getchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


ini = msg.IniAuv()
speed = msg.Speed()
net = net.Net()
while True:
    ch = getchar()
    if ch.strip() == "":
        print("Bye!")
        break
    else:
        print("You pressed", ch)
        if ch == "a":
            speed = msg.Speed(x=-0.5)
            net.set(speed)
        elif ch == "d":
            speed = msg.Speed(x=0.5)
            net.set(speed)
        elif ch == "s":
            speed = msg.Speed(y=-0.9)
            net.set(speed)
        elif ch == "w":
            speed = msg.Speed(y=0.9)
            net.set(speed)
        elif ch == "-":
            speed = msg.Speed(yaw=-30)
            net.set(speed)
        elif ch == "=":
            speed = msg.Speed(yaw=30)
            net.set(speed)
        elif ch == "0":
            ini = msg.IniAuv()
            net.set(ini)
        print(speed)
