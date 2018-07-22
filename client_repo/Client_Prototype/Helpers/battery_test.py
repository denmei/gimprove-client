import datetime
import time
import threading
from pathlib import Path
import os


class BatteryTest(threading.Thread):

    def __init__(self):
        super(BatteryTest, self).__init__()
        self.daemon = True

    def run(self):
        while True:
            test_csv = open(os.path.join(str(Path.home()), "battery_test.csv"), "w+")
            test_csv.write(str(datetime.datetime.now()))
            test_csv.close()
            time.sleep(60)
