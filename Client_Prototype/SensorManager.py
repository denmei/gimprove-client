import time
from threading import Thread
import os


class SensorManager(Thread):

    def __init__(self, set_id, rfid_tag, timer, request_manager, timeout_delta=5):
        self.timeout_delta = timeout_delta
        self.set_id = set_id
        self.rfid_tag = rfid_tag
        self.timer = timer
        self._stop_ = False
        self._rep_ = 0
        self._weight_ = 0
        self.request_manager = request_manager
        Thread.__init__(self)

    def _send_repetition_(self):
        pass

    def stop_thread(self):
        self._stop_ = True

    def get_repetitions(self):
        return self._rep_

    def get_weight(self):
        return self._weight_

    def run(self):
        os.chdir("/home/dennis/PycharmProjects/SmartGym_Client_Prototype/")
        self._rep_ = 0
        self._weight_ = 10
        with open('numbers.txt') as numbers:
            content = numbers.readlines()
        for c in content:
            self.timer.reset_timer()
            self._rep_ += 1
            self.request_manager.update_set(repetitions=self._rep_, weight=self._weight_, set_id=self.set_id,
                                            rfid=self.rfid_tag, active=True)
            time.sleep(0.5)
            if self._stop_:
                break
