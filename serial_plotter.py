"""
Plot live data from serial port using Python, matplotlib and PySerial
"""
import logging
import threading
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class DataWorker(threading.Thread):
    """
    Worker to get date from serial, parse data and put into numpy array
    """
    def __init__(self, ser, data):
        """
        ser: PySerial object
        data: Numpy array to hold data
        """
        threading.Thread.__init__(self)
        self._data = data
        self._ser = ser
        self._running = False
        self._lock = threading.Lock()

    def stop(self):
        self._running = False

    @property
    def snapshot(self):
        """ make a copy of current data and return
        """
        with self._lock:
            data = self._data
        return data

    def run(self):
        """
        Worker loop
        """
        logging.debug("Start running worker")
        self._running = True
        line = ""
        while self._running:
            try:
                if self._ser.is_open:
                    line = self._ser.readline()
            except Exception as e:
                logging.error("Serial port Exception: "+ str(e))
            if line:
                line2 = line.decode("utf-8").strip()
                logging.info(line2)
                if line2 == '':
                    #logging.info("Emtpy line")
                    pass
                elif line2.startswith('#'):
                    logging.info("Found comment line")
                else:
                    self.parseLine(line2)
        logging.debug("Finished running worker")

    def parseLine(self, line):
        """
        Implement your line parsing code here
        This example expects all comma separated values are float
        """
        try:
            values = [float(_) for _ in line.split(',')]
            # make sure the number of values are same as expected
            if len(values) == self._data.shape[0]:
                with self._lock:
                    self._data = np.roll(self._data, -1) # move all data to left by 1
                    self._data[:,-1] = values # replace last data with new values
            else:
                logging.error("Wrong number of values")
                logging.error(line)
        except Exception as e:
            logging.error("error parsing: "+str(e))
            logging.error(line)


class Plotter():
    """
    Class to hold plot figure
    provides functions for animation
    """
    def __init__(self, fig, ax, x_data, data_worker):
        """
        fig: Figure
        ax:
        x_data: array of x values
        n_values: number of values in a line
        n_points: number of x points to plot
        """
        self._x_data = x_data
        self.data_worker = data_worker
        self.fig = fig
        self.ax = ax

    def initial_plot(self):
        """
        Adjust plot command
        Make sure to return lines to update
        """
        # obtain latest data from worker
        data = self.data_worker.snapshot
        # draw a line with 1st row data
        self.lineRed, = self.ax.plot(self._x_data, data[0,:], 'r-')
        # adjust plot
        self.ax.set_xlim(0, 500)
        self.ax.set_ylim(100000,200000)
        return self.lineRed,

    def update_plot(self, frame):
        # obtain latest data from worker
        data = self.data_worker.snapshot
        # update line's ydata
        self.lineRed.set_ydata(data[0,:])
        return self.lineRed,


if __name__ == "__main__":
    fmt = "%(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO)

    port = "/dev/tty.usbmodem14201"
    baudrate = 115200
    ser = serial.Serial(port, baudrate, timeout=1)

    # we expect two values from serial port
    # ValueA,ValueB
    n_values = 2 # expecting number of values in a line
    n_points = 500 # number of latest data points to hold
    # make numpy array to hold data
    arr = np.empty(n_values * n_points)
    arr[:] = np.nan # fill with NaN as default
    data = np.reshape(arr, (n_values, n_points))

    arr_x = np.arange(n_points) # make array for x axis

    fig = plt.figure()
    ax = fig.add_subplot(111)
    dataworker = DataWorker(ser, data)
    plotter = Plotter(fig, ax, arr_x, dataworker)
    dataworker.start()
    ani = FuncAnimation(fig, 
                        plotter.update_plot, 
                        frames=None,
                        init_func=plotter.initial_plot, 
                        blit=True, 
                        interval=50,
                        )
    plt.show()
    dataworker.stop()
