# serial_plotter
Plot live data from serial port using Python, matplotlib and PySerial

Idea is to use only basic libraries (matplotlib and PySerial) to make real time plotting.

It seems a simple task that reading data from serial port and updating plot quickly. But it actually takes a bit of thinking... how to read data from serial port without blocking UI (= threading) and how to update plot quickly on matplotlib (= animation).

This is meant to be a boiler plate code. Please modify to your liking.
