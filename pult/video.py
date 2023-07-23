import io
import socket
import sys
import threading
import tkinter
from tkinter import ttk

import setproctitle
from PIL import Image, ImageTk

PORT_FRONT = 1111
PORT_BOTTOM = 1112

setproctitle.setproctitle(' '.join(sys.argv))

root = tkinter.Tk()
root.title('Camera ' + sys.argv[1])
root.geometry("1920x1080")

image_label = tkinter.Label(root)
image_label.pack()

sock_set = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if sys.argv[1] == 'Front':
    sock_set.bind(('', PORT_FRONT))
elif sys.argv[1] == 'Bottom':
    sock_set.bind(('', PORT_BOTTOM))
else:
    exit()

close = threading.Event()

def closeApp():
    close.set()

root.protocol("WM_DELETE_WINDOW", closeApp)

root.update()
root.update_idletasks()

while True:
    if close.is_set():
        break

    buf, addr = sock_set.recvfrom(65535)
    print(sys.getsizeof(buf))

    imageStream = io.BytesIO(buf)
    image_real = Image.open(imageStream)
    image = image_real.resize((1920, 1080))

    try:
        image_tk = ImageTk.PhotoImage(image)
        image_label['image'] = image_tk
    except:
        pass
    
    root.update()
    root.update_idletasks()
