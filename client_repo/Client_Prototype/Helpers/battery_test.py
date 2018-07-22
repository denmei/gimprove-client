import datetime
import time
import threading
from pathlib import Path
import os


class BatteryTest(threading.Thread):

    def __init__(self):
        super(BatteryTest, self).__init__()
        print(os.path.join(str(Path.home()), "battery_test.csv"))
        self.daemon = True
        self.test_csv = open(os.path.join(str(Path.home()), "battery_test.csv"), "w+")

    def run(self):
        while True:
            self.test_csv.write(str(datetime.datetime.now()))
            time.sleep(60)
