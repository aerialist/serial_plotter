import tkinter as tk
from tkinter import scrolledtext
import serial
import asyncio
import threading

class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication")

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10, state='disabled')
        self.text_area.grid(column=0, row=0, padx=10, pady=10, columnspan=3)

        self.input_box = tk.Entry(root, width=30)
        self.input_box.grid(column=0, row=1, padx=10, pady=10)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(column=1, row=1, padx=10, pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_application)
        self.exit_button.grid(column=2, row=1, padx=10, pady=10)

        self.serial_port = serial.Serial('/dev/tty.usbmodem64327301', 9600, timeout=1)  # Adjust this as per your serial port

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, args=(self.loop,))
        self.thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.read_serial())

    async def read_serial(self):
        while True:
            if self.serial_port.in_waiting > 0:
                message = self.serial_port.readline().decode('utf-8').strip()
                self.update_text_area(message)
            await asyncio.sleep(0.1)

    def update_text_area(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')

    def send_message(self):
        message = self.input_box.get()
        if message:
            self.serial_port.write(message.encode('utf-8'))
            self.input_box.delete(0, tk.END)

    def exit_application(self):
        self.loop.stop()
        self.serial_port.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCommunicationApp(root)
    root.mainloop()
