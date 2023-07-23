import sys
import threading
import time
import tkinter
from tkinter import BOTH, ttk

import setproctitle
from PIL import Image, ImageTk

sys.path.append('./')
from base import message, network

TIMER = 0.05


class App(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.net = network.Net()
        self.message = message.Control()
        self.stop_thread_event = threading.Event()

        self.send_thread = threading.Thread(target=self.sendCall)
        self.send_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.closeApp)

        self.title('System Diagnotics')
        self.geometry('600x600')
        self.resizable(False, False)

        self.appFrame = ttk.Frame(self)
        self.appFrame.pack(fill='both', expand=True)
        
        self.initData()

        self.loadStart()

    def initData(self):
        self.index = 0

        self.data = [ 
                      ( 'pictures/left_3.png',  [ 1, 0, 0, 0, 0, 0 ] ), 
                      ( 'pictures/right_3.png', [ 0, 1, 0, 0, 0, 0 ] ),
                      ( 'pictures/left_2.png',  [ 0, 0, 1, 0, 0, 0 ] ),
                      ( 'pictures/right_2.png', [ 0, 0, 0, 1, 0, 0 ] ),
                      ( 'pictures/left_1.png',  [ 0, 0, 0, 0, 1, 0 ] ),
                      ( 'pictures/right_1.png', [ 0, 0, 0, 0, 0, 1 ] ),
                      ( 'pictures/turn_2.jpg',  [ 0, 0, 0, 0, 0, 0 ] ),
                    ]

    def sendCall(self):
        while True:
            if self.stop_thread_event.is_set():
                break

            self.net.send(self.message)
            
            time.sleep(TIMER) 

    def closeApp(self):
        self.stop_thread_event.set()
        self.send_thread.join()
        self.destroy()

    def clearFrame(self):
        for widgets in self.appFrame.winfo_children():
            widgets.destroy()

    def loadStart(self):
        self.startButton = ttk.Button(self.appFrame, text='Начать', command=self.loadKotleta)
        self.startButton.place(relx=0.5, rely=0.5, anchor='center')

    def loadKotleta(self):
        self.clearFrame()

        self.message.power = self.data[self.index][1]

        for c in range(3): self.appFrame.columnconfigure(index=c, weight=1)
        for r in range(3): self.appFrame.rowconfigure(index=r, weight=1)

        self.image_label = ttk.Label(self.appFrame)
        self.image_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.text_label = ttk.Label(self.appFrame, text='Кручение соответствует картинке?', font=("Arial", 12))
        self.text_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.yesButton = ttk.Button(self.appFrame, text='Да', command=self.kotletaYesButtonHandle)
        self.yesButton.grid(row=2, column=0, padx=10, pady=10, sticky='e')

        self.noButton = ttk.Button(self.appFrame, text='Нет', command=self.kotletaNoButtonHandle)
        self.noButton.grid(row=2, column=2, padx=10, pady=10, sticky='w')

        self.setImage()

    def loadSensors(self):
        self.clearFrame()

        self.message.power = self.data[self.index][1]

        for c in range(3): self.appFrame.columnconfigure(index=c, weight=1)
        for r in range(3): self.appFrame.rowconfigure(index=r, weight=1)

        self.image_label = ttk.Label(self.appFrame)
        self.image_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.text_label = ttk.Label(self.appFrame, text='Поверните АНПА влево на 90 градусов.', font=("Arial", 12))
        self.text_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.yesButton = ttk.Button(self.appFrame, text='Готово', command=self.sensorsReadyButtonHandle, width=20)
        self.yesButton.grid(row=2, column=0, padx=10, pady=10, sticky='e')

        self.noButton = ttk.Button(self.appFrame, text='Отменить проверку', command=self.sensorsCancelButtonHandle, width=20)
        self.noButton.grid(row=2, column=2, padx=10, pady=10, sticky='w')

        self.setImage()

    def loadResult(self):
        self.clearFrame()

        for c in range(2): self.appFrame.columnconfigure(index=c, weight=1)
        for r in range(3): self.appFrame.rowconfigure(index=r, weight=1)

        kotleta_label = ttk.Label(self.appFrame, text='ДРК', font=("Arial", 12), width=25, anchor='center')
        kotleta_label.grid(row=0, column=0)

        success_kotleta_label = ttk.Label(self.appFrame, text='проверка успешна', font=("Arial", 12), foreground='#008000')
        success_kotleta_label.grid(row=0, column=1)

        sensor_label = ttk.Label(self.appFrame, text='Навигационные датчики', font=("Arial", 12), width=25, anchor='center')
        sensor_label.grid(row=1, column=0)

        success_sensor_label = ttk.Label(self.appFrame, text='проверка успешна', font=("Arial", 12), foreground='#008000')
        success_sensor_label.grid(row=1, column=1)

        photo_label = ttk.Label(self.appFrame, text='Фотосистема', font=("Arial", 12), width=25, anchor='center')
        photo_label.grid(row=2, column=0)

        success_photo_label = ttk.Label(self.appFrame, text='проверка успешна', font=("Arial", 12), foreground='#008000')
        success_photo_label.grid(row=2, column=1)

    def setImage(self):
        self.image = Image.open(self.data[self.index][0])
        self.image = self.image.resize((self.image.width // 2, self.image.height // 2), Image.LANCZOS)
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_label['image'] = self.image_tk

    def kotletaYesButtonHandle(self):
        self.index += 1
        self.message.power = self.data[self.index][1]

        if self.index >= 6:
            self.loadSensors()
            return

        self.setImage()

    def kotletaNoButtonHandle(self):
        self.kotletaYesButtonHandle()
        self.kotletaDiagnoticsSuccess = False

    def sensorsReadyButtonHandle(self):
        self.loadResult()

    def sensorsCancelButtonHandle(self):
        pass


def main():
    setproctitle.setproctitle(' '.join(sys.argv))

    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
