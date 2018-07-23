import datetime
import time
import threading
from pathlib import Path
import os
import datetime


class BatteryTest(threading.Thread):

    def __init__(self):
        super(BatteryTest, self).__init__()
        self.file_name = "battery_test_" + str(datetime.datetime.now()).replace(" ", "_") + ".csv"
        self.daemon = True

    def run(self):
        while True:
            test_csv = open(os.path.join(str(Path.home()), self.file_name), "w+")
            test_csv.write(str(datetime.datetime.now()))
            test_csv.close()
            time.sleep(60)
