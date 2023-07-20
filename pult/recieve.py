from PIL import Image, ImageTk
import socket, sys, io, threading

import tkinter
from tkinter import ttk

PORT_FRONT = 1111
PORT_BOTTOM = 1112

root = tkinter.Tk()
root.title("Camera")
root.geometry("1920x1080")

image_label = tkinter.Label(root)
image_label.pack()

sock_set = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_set.bind(('', 1112))

root.update()
root.update_idletasks()

while True:
    buf, addr = sock_set.recvfrom(65535)
    print(sys.getsizeof(buf))

    imageStream = io.BytesIO(buf)
    image_real = Image.open(imageStream)
    image = image_real.resize((1920, 1080))

    # crop = image.crop((62, 0, 962, 512))

    try:
        image_tk = ImageTk.PhotoImage(image)
        image_label['image'] = image_tk
    except:
        pass
    
    root.update()
    root.update_idletasks()


# def recieve_photo_thread(image_label, port, close_event): 
#     sock_set = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
#     sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
#     sock_set.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock_set.bind(('', port))

#     while True:
#         if close_event.is_set():
#             break

#         buf, addr = sock_set.recvfrom(65535)
#         print(sys.getsizeof(buf))

#         imageStream = io.BytesIO(buf)
#         image_real = Image.open(imageStream)
#         image = image_real.resize((1024, 512))

#         crop = image.crop((62, 0, 962, 512))

#         try:
#             image_tk = ImageTk.PhotoImage(crop)
#             image_label['image'] = image_tk
#         except:
#             pass


# def main():
#     root = tkinter.Tk()
#     root.title("Camera")
#     root.geometry("1920x1080")

#     for c in range(2): root.columnconfigure(index=c, weight=1)
#     for r in range(2): root.rowconfigure(index=r, weight=1)

#     front_left = ttk.Label(root) 
#     front_left.grid(row=0, column=0)

#     front_right = ttk.Label(root) 
#     front_right.grid(row=0, column=1)

#     bottom_left = ttk.Label(root) 
#     bottom_left.grid(row=1, column=0)

#     bottom_right = ttk.Label(root) 
#     bottom_right.grid(row=1, column=1)

#     front_left_event = threading.Event()
#     front_right_event = threading.Event()
#     bottom_left_event = threading.Event()
#     bottom_right_event = threading.Event()

#     front_left_thread = threading.Thread(target=recieve_photo_thread, args=(front_left, PORT_FRONT_LEFT, front_left_event))
#     front_right_thread = threading.Thread(target=recieve_photo_thread, args=(front_right, PORT_FRONT_RIGHT, front_right_event))
#     bottom_left_thread = threading.Thread(target=recieve_photo_thread, args=(bottom_left, PORT_BOTTOM_LEFT, bottom_left_event))
#     bottom_right_thread = threading.Thread(target=recieve_photo_thread, args=(bottom_right, PORT_BOTTOM_RIGHT, bottom_right_event))

#     front_left_thread.start()
#     front_right_thread.start()
#     bottom_left_thread.start()
#     bottom_right_thread.start()

#     def closeApp():
#         front_left_event.set()
#         front_right_event.set()
#         bottom_left_event.set()
#         bottom_right_event.set()

#         root.destroy()

#     root.protocol("WM_DELETE_WINDOW", closeApp)
#     root.mainloop()

#     front_left_thread.join()
#     front_right_thread.join()
#     bottom_left_thread.join()
#     bottom_right_thread.join()


# if __name__ == '__main__':
#     main()
