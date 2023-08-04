import sys
import threading
import time

import setproctitle
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)

sys.path.append('./')
from base import message as m
from base import network
from base.timer import Timer


class Command(QWidget):
    def __init__(self, message: m.Message):
        super().__init__()

        self.message = message
        self.name = message.id
        self.is_timer = False
        self.timer = Timer(0.1)
        self.send_active = False

        arguments = message.__init__.__code__.co_varnames[1:]
        values = message.__init__.__defaults__

        main_layout = QHBoxLayout()
        main_layout.addSpacing(10)

        name = QLabel(self.name)
        name.setMinimumWidth(150)
        main_layout.addWidget(name)

        item_hbox = QHBoxLayout()
        item_hbox.addSpacing(10)

        self.line_edits = []
        for i in range(len(arguments)):
            layout = QHBoxLayout()
            label = QLabel(arguments[i])
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            line_edit = QLineEdit(str(values[i]))
            line_edit.setMinimumWidth(100)

            self.line_edits.append(line_edit)

            layout.addWidget(label)
            layout.addWidget(line_edit)

            item_hbox.addLayout(layout)
            item_hbox.addSpacing(10)

        scroll_widget = QWidget()
        scroll_widget.setLayout(item_hbox)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        main_layout.addSpacing(10)

        buttons = QHBoxLayout()

        timer = QCheckBox('Timer')
        timer.stateChanged.connect(self.onTimerChecked)
        timer_edit = QDoubleSpinBox()
        timer_edit.valueChanged.connect(self.onTimerValueChanged)
        timer_edit.setSingleStep(0.01)
        timer_edit.setDecimals(3)
        timer_edit.setMinimum(0.000)
        timer_edit.setMaximum(60)
        buttons.addWidget(timer)
        buttons.addWidget(timer_edit)
        buttons.addSpacing(10)

        send = QPushButton('Send')
        send.clicked.connect(self.onSendClicked)
        buttons.addWidget(send)
        main_layout.addLayout(buttons)

        self.setLayout(main_layout)

    def parse(self, value: str):
        if value == 'None':
            return None
        
        try:
            return int(value)
        except:
            pass
            
        try:
            return float(value)
        except:
            pass

        return value

    def getMessage(self):   
        arguments = []
        for i in range(len(self.line_edits)):
            value = self.parse(self.line_edits[i].text())
            arguments.append(value)

        self.message.__init__(*arguments)
        return self.message

    @pyqtSlot()
    def onSendClicked(self):
        self.send_active = True

    @pyqtSlot(int)
    def onTimerChecked(self, state):
        self.is_timer = bool(state)

    @pyqtSlot(float)
    def onTimerValueChanged(self, value):
        self.timer = Timer(value)


class MainWindow(QMainWindow):
    messages = [
                m.Sensor(), 
                m.SensorRU(), 
                m.Coord(), 
                m.Tack(),
                m.Motion(), 
                m.Control(), 
                m.InitRobot(), 
                m.InitObject(), 
                m.ResetObjects(), 
                m.DetectionOn(), 
                m.DetectionOff(), 
                m.DetectedObject(), 
                m.FilteredObjects(), 
                m.ImageLink(),
                m.PhotoOn(),
                m.PhotoOff(),
                m.SoundDelay(),
                m.KeyOn(),
                m.KeyOff(),
                m.OdometryRaw(),
               ]

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Command')

        item_vbox = QVBoxLayout()
        self.commands = []
        for it in self.messages:
            command = Command(it)
            self.commands.append(command)
            item_vbox.addWidget(command)

        scroll_widget = QWidget()
        scroll_widget.setLayout(item_vbox)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
    
        self.setCentralWidget(scroll_area)

        self.close_event = threading.Event()

    def closeEvent(self, event):
        self.close_event.set()

        super().closeEvent(event)

    def sendCycle(self):
        net = network.Net()
        while True:
            if self.close_event.is_set():
                break

            for it in self.commands:
                if not it.send_active:
                    continue

                if not it.is_timer:
                    net.send(it.getMessage())
                    it.send_active = False
                    continue

                if it.timer.is_unlock:
                    net.send(it.getMessage())

            QApplication.instance().processEvents()

            time.sleep(0.0005)


def main(): 
    setproctitle.setproctitle(' '.join(sys.argv))

    app = QApplication([])

    window = MainWindow()
    window.show()
    window.sendCycle()

    app.exec()


if __name__ == '__main__':
    main()
