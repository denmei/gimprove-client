import matplotlib.pyplot as plt
import time

class StreamPlotter:

    def __init__(self):
        self.fig = plt.figure()
        self.min = 0
        self.max = 0
        self.plot_data, = plt.plot([])
        self.fig.show()

    def update(self, data):
        # plt.pause(0.01)
        print(len(data))
        print(len(range(len(data))))
        self.plot_data.set_xdata(range(len(data)))
        self.plot_data.set_ydata(data)
        plt.draw()
