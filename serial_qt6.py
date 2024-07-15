import sys
import serial
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QTextCursor

# Define your serial port here
SERIAL_PORT = '/dev/tty.usbmodem64327301'

class SerialThread(QThread):
    message_received = Signal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self._running = True

    def run(self):
        while self._running:
            if self.serial_port.in_waiting > 0:
                message = self.serial_port.readline().decode('utf-8').strip()
                self.message_received.emit(message)

    def stop(self):
        self._running = False
        self.wait()

class SerialCommunicationApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Serial Communication")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)

        self.input_box = QLineEdit()
        self.layout.addWidget(self.input_box)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_application)
        self.layout.addWidget(self.exit_button)

        self.serial_port = serial.Serial(SERIAL_PORT, 9600, timeout=1)

        self.serial_thread = SerialThread(self.serial_port)
        self.serial_thread.message_received.connect(self.update_text_area)
        self.serial_thread.start()

    @Slot(str)
    def update_text_area(self, message):
        self.text_area.append(message)
        self.text_area.moveCursor(QTextCursor.End)

    def send_message(self):
        message = self.input_box.text()
        if message:
            self.serial_port.write(message.encode('utf-8'))
            self.input_box.clear()

    def exit_application(self):
        self.serial_thread.stop()
        self.serial_port.close()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialCommunicationApp()
    window.show()
    sys.exit(app.exec())
