import time
from threading import Thread


class Timer(Thread):
    """
    Provides timeout functionality, running in an own thread.
    """

    def __init__(self, time_out):
        self._time_out_ = time_out
        self.timed_out = False
        self.timer = self._time_out_
        Thread.__init__(self)
        self.daemon = True
        self._stop_ = False

    def reset_timer(self):
        """
        Resets the timer to its time_out value.
        """
        self.timer = self._time_out_
        self.timed_out = False

    def get_timer(self):
        """
        :return: Current value of the timer.
        """
        return self.timer

    def is_timed_out(self):
        """
        :return: True if timer is timed out, False else.
        """
        return self.timed_out

    def stop_timer(self):
        self._stop_ = True

    def run(self):
        """
        Starts the timer.
        """
        self.timed_out = False
        self.timer = self._time_out_
        while self.timer > 0 and not self._stop_:
            self.timer -= 1
            time.sleep(1)
        self.timed_out = True
