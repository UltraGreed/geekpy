from base import network, message
from base.message import ImageLink
import threading

from PyQt6.QtMultimedia import QCamera, QMediaDevices, QImageCapture, QMediaCaptureSession
from PyQt6.QtGui        import QPixmap
from PyQt6.QtWidgets    import QApplication, QWidget, QHBoxLayout, QGraphicsScene, QGraphicsView
from PyQt6.QtCore       import QTimer
import sys


class MainWindow(QWidget):
    
    def __init__(self, fps = 10):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PyQt6 Camera test")
        self.setGeometry(0,0,720*2,750)
        #Internal variables
        self.counter = 0

        #Gui
        self.layout = QHBoxLayout(self)
        
        self.camera_device = QMediaDevices.defaultVideoInput()
        self.camera        = QCamera(self.camera_device)

        self.capture_session = QMediaCaptureSession()
        self.capture_session.setCamera(self.camera)
        
        self.image_capture = QImageCapture(self.camera)
        self.capture_session.setImageCapture(self.image_capture)

        self.camera.start()
        self.img_raw = QPixmap()

        self.img_left = QGraphicsScene()
        self.left_pixmap = self.img_left.addPixmap(self.img_raw)
        self.img_left_view = QGraphicsView(self.img_left)
        self.layout.addWidget(self.img_left_view)

        self.img_right = QGraphicsScene()
        self.right_pixmap = self.img_right.addPixmap(self.img_raw)
        self.img_right_view = QGraphicsView(self.img_right)
        self.layout.addWidget(self.img_right_view)

        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.errorOccurred.connect(self.error)

        self.net = network.Net()

        self.fps_timer = QTimer()
        self.fps_timer.setInterval(int(1.0/fps * 1000.0)) 
        self.fps_timer.setSingleShot(False)
        self.fps_timer.timeout.connect(self.capture_image)
        self.fps_timer.start()

        self.right_path = None
        self.received = False

        self.net_thread = threading.Thread(target = self.receive_picture)
        self.net_thread.start()

    def error(self, id, error, error_string):
        print(error_string)

    def capture_image(self):
        self.image_capture.capture() 

    def receive_picture(self):
        while self.net.receive():
            if self.net.id == "ImageLink":
                if self.net.msg.obj == "NN_CellB":
                    self.right_path = self.net.msg.path     
                    self.received = True       

    def image_captured(self, id, image):   
        pixmap = QPixmap.fromImage(image).copy(280,0,720,720)
        self.left_pixmap.setPixmap(pixmap)

        self.counter += 1
        self.counter %= 20
        pixmap.scaled(256,256).save(f"debug/{self.counter:05d}.png")
        
        self.net.send(ImageLink(
            obj  = "Bottom",
            path = f"debug/{self.counter:05d}.png",
            file = f"{self.counter:05d}.png",
            counter = self.counter
        ))

        while self.received == False:
            pass

        if self.right_path != None:
            pixmap = QPixmap()
            pixmap.load(self.right_path)
            pixmap = pixmap.scaled(720,720)
            self.right_pixmap.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
    