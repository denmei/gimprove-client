import time
from threading import Thread
import os
from datetime import datetime
import logging
from pathlib import Path
from hx711py.hx711 import HX711


class SensorManager(Thread):

    def __init__(self, set_id, rfid_tag, timer, request_manager, min_dist, max_dist, timeout_delta=5, testing=True):
        """
        Responsible for tracking the repetitions and weight using the sensor data.
        :param set_id: ID of the current set.
        :param rfid_tag: RFID tag of the active user.
        :param timer: Reference on the Timer module that stops the process on inactivity.
        :param request_manager: Reference on the request manager for sending updates to the server.
        :param min_dist: minimum value that has to be reached with the distance sensor to count a repetition.
        :param max_dist: maximum value the distance sensor can reach.
        :param timeout_delta: If 'timeout_delta' seconds pass without a new repetition, the process stops.
        :param testing: If true, executes in testing mode (uses sensor data). Otherwise, local files are used to
        simulate the sensor input.
        """
        self.logger = logging.getLogger('gimprove' + __name__)
        if not testing:
            self._init_hx_weight_()
        self.timeout_delta = timeout_delta
        self.set_id = set_id
        self.rfid_tag = rfid_tag
        self.timer = timer
        self._stop_ = False
        self._rep_ = 0
        self._min_ = min_dist
        self._max_ = max_dist
        self.request_manager = request_manager
        self._durations_ = []
        self._start_time_ = datetime.now()
        self.testing = testing
        # buffer for the measured distances
        # Todo: limit size (FIFO)
        self._distance_buffer_ = []
        # TODO: delete:
        self._no_ = 0
        self._numbers_file_ = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + '/numbers.txt'
        Thread.__init__(self)
        self.daemon = True

    def _init_hx_weight_(self):
        self.hx_weight = HX711(5, 6)
        self.hx_weight.set_reading_format("LSB", "MSB")
        self.hx_weight.set_reference_unit(92)
        self.hx_weight.reset()
        self.hx_weight.tare()

    def stop_thread(self):
        """
        Stops the sensormanager.
        """
        self._stop_ = True

    def get_repetitions(self):
        """
        Returns the current count of repetitions.
        """
        return self._rep_

    def get_weight(self):
        """
        Returns the current weight measured.
        """
        if self.testing:
            return 10
        else:
            weight = self.hx_weight.get_weight(5)
            print("Weightsensor: " + str(weight))
            return weight

    def _check_reps_(self, repetitions, distance_buffer):
        """
        Gets distance from distance sensor. Checks whether new repetition has been made. Updates the passed repetitions
        parameter and the distance buffer.
        :param repetitions: Current count of repetitions to be updated.
        :param distance_buffer: Current collection of measured distances to be updated
        :return: [updated repetitions, updated distance_buffer]
        """
        # get current distance from distance sensor.
        # TODO: currently reading from txt file, replace by sensor
        with open(self._numbers_file_) as numbers:
            print("NO: " + str(self._no_))
            lines = numbers.readlines()
            length = len(lines)
            distance = lines[self._no_]
        self._no_ += 1
        if self._no_ >= length:
            self._stop_ = True
        # update distance buffer
        distance_buffer += [int(distance)]
        # calculate repetitions and update repetitions-value
        new_reps = max(self._analyze_distance_buffer_(distance_buffer), repetitions)
        return new_reps, distance_buffer

    def _analyze_distance_buffer_(self, distance_buffer):
        """
        Counts the number of repetitions in a distance buffer. Simple logic that has to be replaced: Counts if a
         distance is smaller than the min-Value. Then waits until half of the distance between min and max has been
         reached again.
        :return: Number of repetitions in the buffer.
        """
        # TODO: Find algorithm to analyze distance buffer properly
        count = 0
        threshold = (self._max_ - self._min_)/2
        no_count = False
        for distance in distance_buffer:
            print(distance + 1)
            if (distance < self._min_) and (no_count is False):
                count += 1
                no_count = True
            elif distance > threshold and no_count:
                no_count = False
            else:
                pass
        return count

    def get_durations(self):
        """
        Returns the durations of the current repetitions.
        """
        return self._durations_

    def _update_durations_starttime_(self, durations, start_time):
        """
        Updates the durations of the repetitions.
        """
        durations = durations + [(datetime.now() - start_time).total_seconds()]
        return durations, datetime.now()

    def run(self):
        """
        While running, the values of the distance sensor are analyzed. If a new repetition is identified, the current
        value of the weight sensor is taken and a new repetition-request is sent to the server.
        """
        self.logger.info("Start recording.")
        self._rep_ = 0
        while not self._stop_:
            self.timer.reset_timer()
            # update repetitions
            old_rep = self._rep_
            self._rep_, self._distance_buffer_ = self._check_reps_(self._rep_, self._distance_buffer_)
            # if new repetition, update all other values
            if old_rep != self._rep_:
                # update durations
                self._durations_, self._start_time_ = self._update_durations_starttime_(self._durations_,
                                                                                        self._start_time_)
                # send update
                self.request_manager.update_set(repetitions=self._rep_, weight=self.get_weight(), set_id=self.set_id,
                                                rfid=self.rfid_tag, active=True, durations=self._durations_)
            time.sleep(0.1)
        print("Final: rep: " + str(self._rep_) + " Durations: " + str(self._durations_))
        self.logger.info('Timeout. Stop recording.')
