import matplotlib.pyplot as plt
import time


class StreamPlotter:

    def __init__(self, distance_buffer, sleep):
        self.fig = plt.figure()
        self.min = 0
        self.max = 0
        self.distance_buffer = distance_buffer
        self.timer_sleep = sleep
        self.plot_data = plt.plot()

    def set_min_line(self, y):
        pass

    def set_max_line(self, y):
        pass

    def run(self):
        self.fig.show()
        while True:
            self.fig.canvas.pause()
            self.plot_data.set_xdata(range(len(self.distance_buffer)))
            self.plot_data.set_ydata(self.distance_buffer)
            self.fig.canvas.draw()
            time.sleep(self.timer_sleep)
