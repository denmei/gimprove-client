import time
from threading import Thread
import os


class SensorManager(Thread):

    def __init__(self, set_id, rfid_tag, timer, timeout_delta=5):
        self.timeout_delta = timeout_delta
        self.set_id = set_id
        self.rfid_tag = rfid_tag
        self.timer = timer
        Thread.__init__(self)

    def _send_repetition_(self):
        pass

    def run(self):
        os.chdir("/home/dennis/PycharmProjects/SmartGym_Client_Prototype/")
        rep = 0
        weight = 0
        with open('numbers.txt') as numbers:
            content = numbers.readlines()
        for c in content:
            self.timer.reset_timer()
            print("Sensor: " + str(c))
            rep += 1
            weight = 0
            time.sleep(0.5)
