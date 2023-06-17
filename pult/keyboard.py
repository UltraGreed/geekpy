#!python3 keyboard.py
import time, tty, termios, sys, setproctitle
sys.path.append('../base')
import network, message

def getchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
   
setproctitle.setproctitle(sys.argv[0])  # Set filename.py title for process.
net = network.Net()

while True:

    ch = getchar()
    print("You pressed", ch)
    if ch.strip() == "": print("Bye!"); break

    # elif ch == "a": net.send(message.Motion(x= -0.5))
    # elif ch == "d": net.send(message.Motion(x=  0.5))
    # elif ch == "s": net.send(message.Motion(y= -0.9))
    # elif ch == "w": net.send(message.Motion(y=  0.9))
    # elif ch == "-": net.send(message.Motion(yaw=-30))
    # elif ch == "=": net.send(message.Motion(yaw= 30))

    elif ch == "a": net.send(message.Tack(speed_x= -0.5))
    elif ch == "d": net.send(message.Tack(speed_x=  0.5))
    elif ch == "s": net.send(message.Tack(speed_y= -0.9))
    elif ch == "w": net.send(message.Tack(speed_y=  0.9))
    elif ch == "-": net.send(message.Tack(speed_yaw=-30))
    elif ch == "=": net.send(message.Tack(speed_yaw= 30))

    elif ch == "0": net.send(message.InitRobot(x=0.0, y=0.0, depth=0.0, yaw=0.0))

    elif ch == "1": net.send(message.Tack(time=5, stab_yaw=  0.0))
    elif ch == "2": net.send(message.Tack(time=5, stab_yaw= 45.0))
    elif ch == "3": net.send(message.Tack(time=5, stab_yaw= 90.0))
    elif ch == "4": net.send(message.Tack(time=5, stab_yaw=135.0))
    elif ch == "5": net.send(message.Tack(time=5, stab_yaw=180.0))
    elif ch == "6": net.send(message.Tack(time=5, stab_yaw=225.0))
    elif ch == "7": net.send(message.Tack(time=5, stab_yaw=270.0))
    elif ch == "8": net.send(message.Tack(time=5, stab_yaw=315.0))
    elif ch == "9": net.send(message.Tack(time=5, stab_yaw=360.0))

    elif ch == "f": net.send(message.Tack(time=5, stab_x=-2))
    elif ch == "h": net.send(message.Tack(time=5, stab_x= 2))
    elif ch == "g": net.send(message.Tack(time=5, stab_y=-2))
    elif ch == "t": net.send(message.Tack(time=5, stab_y= 2))

    elif ch == "i": net.send(message.Tack(time=5, stab_x=-2, stab_y= 2))
    elif ch == "o": net.send(message.Tack(time=5, stab_x= 2, stab_y= 2))
    elif ch == "k": net.send(message.Tack(time=5, stab_x=-2, stab_y=-2))
    elif ch == "l": net.send(message.Tack(time=5, stab_x= 2, stab_y=-2))
