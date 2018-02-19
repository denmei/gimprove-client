import time
from threading import Thread
import os
from datetime import datetime
import logging


class SensorManager(Thread):

    def __init__(self, set_id, rfid_tag, timer, request_manager, timeout_delta=5):
        """
        Responsible for tracking the repetitions and weight using the sensor data.
        :param set_id: ID of the current set.
        :param rfid_tag: RFID tag of the active user.
        :param timer: Reference on the Timer module that stops the process on inactivity.
        :param request_manager: Reference on the request manager for sending updates to the server.
        :param timeout_delta: If 'timeout_delta' seconds pass without a new repetition, the process stops.
        """
        self.logger = logging.getLogger('gimprove' + __name__)
        self.timeout_delta = timeout_delta
        self.set_id = set_id
        self.rfid_tag = rfid_tag
        self.timer = timer
        self._stop_ = False
        self._rep_ = 0
        self._weight_ = 10
        self.request_manager = request_manager
        self.durations = []
        self._start_time_ = datetime.now()
        Thread.__init__(self)

    def _send_repetition_(self):
        pass

    def stop_thread(self):
        self._stop_ = True

    def get_repetitions(self):
        return self._rep_

    def get_weight(self):
        return self._weight_

    def get_durations(self):
        return self.durations

    def _update_durations_starttime_(self, durations, start_time):
        durations = durations + [(datetime.now() - start_time).total_seconds()]
        return durations, datetime.now()

    def run(self):
        """
        While running, the values of the distance sensor are analyzed. If a new repetition is identified, the current
        value of the weight sensor is taken and a new repetition-request is sent to the server.
        """
        self.logger.info("Start recording.")
        os.chdir("/home/dennis/PycharmProjects/SmartGym_Client_Prototype/")
        self._rep_ = 0
        self._weight_ = 10
        with open('numbers.txt') as numbers:
            content = numbers.readlines()
        for c in content:
            self.timer.reset_timer()
            self._rep_ += 1
            self.durations, self._start_time_ = self._update_durations_starttime_(self.durations, self._start_time_)
            self.request_manager.update_set(repetitions=self._rep_, weight=self._weight_, set_id=self.set_id,
                                            rfid=self.rfid_tag, active=True, durations=self.durations)
            time.sleep(1.5)
            if self._stop_:
                self.logger.info('Timeout. Stop recording.')
                break
