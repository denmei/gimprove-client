import os
from datetime import datetime
import datetime as dt
import logging
from pathlib import Path
from hx711py.hx711 import HX711
import numpy as np
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import pandas as pd


class SensorManager:
    """
    Responsible for recording and analyzing the sensor data during one session. Running in a own thread, the
    SensorManager records the sensor-activity until the session is timed out (no new repetition).
    When a new repetition is recognized, the weight from the weight sensor is taken and a new request to update the
    current set with the new data is sent to the server.

    In testing mode, the distance data from the distance.csv-file is taken, while the weight will always be 10.

    During the whole session, all distance-data is collected in _distance_buffer_. So every time the SensorManager
    analyzes the current set looking for new repetitions, all available data from the current session is used (should
    be changed in the future to increase performance).
    """

    def __init__(self, queue, min_dist, max_dist, dout=5, pd_sck=6, gain=128, byte_format="LSB", bit_format="MSB",
                 reference_unit=92, timeout_delta=10, use_sensors=False, plot_len=60, rep_val=0.8, frequency=0.01, offset=1,
                 address=0x29, TCA9548A_Num=255, TCA9548A_Addr=0, ranging_mode="VL53L0X_BETTER_ACCURACY_MODE", plot=False,
                 print_distance=True, print_weight=True, print_undermax=False, final_plot=False,
                 weight_translation=False,
                 distances_file=str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + '/distances.csv',
                 weights_file=str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + '/weights.csv'):
        """
        Responsible for tracking the repetitions and weight using the sensor data.
        :param queue: Reference on the message queue where messages can be sent from.
        :param min_dist: minimum value that has to be reached with the distance sensor to count a repetition.
        :param max_dist: maximum value the distance sensor can reach.
        :param byte_format: order in which the bytes are used to build the "long" value.
        :param bit_format: order of the bits inside each byte.
        :param timeout_delta: If 'timeout_delta' seconds pass without a new repetition, the process stops.
        """
        self.logger = logging.getLogger('gimprove' + __name__)
        if use_sensors:
            GPIO.cleanup()
            self.ranging_mode = self._init_vl530_distance_(address=address, TCA9548A_Num=TCA9548A_Num, TCA9548A_Addr=TCA9548A_Addr,
                                       mode=ranging_mode)
            self._init_hx_weight_(dout=dout, pd_sck=pd_sck, gain=gain, byte_format=byte_format, bit_format=bit_format,
                                  offset=offset, reference_unit=reference_unit)
        self.timeout_delta = timeout_delta
        self.time_out_time = datetime.now() + dt.timedelta(seconds=timeout_delta)
        self.plot_len = plot_len
        self.rep_val = rep_val
        self.frequency = frequency
        self._stop_ = False
        self._rep_ = 0
        self._min_ = min_dist
        self._max_ = max_dist
        self.queue = queue
        self._durations_ = []
        self._start_time_ = datetime.now()
        self.use_sensors = use_sensors
        self.plot = plot
        self.print_distance = print_distance
        self.print_weight = print_weight
        self.print_undermax = print_undermax
        self.final_plot = final_plot
        if weight_translation:
            self.weight_translation = self.get_weight_translation()
        else:
            self.weight_translation = None
        # buffer for the measured distances
        # Todo: limit size (FIFO)
        self._distance_buffer_ = []
        self._total_distances_ = []

        # only for testing:
        self._weight_ = 0
        self._weight_list_ = []
        self._no_ = 0
        self._numbers_file_ = distances_file
        self._weights_file_ = weights_file

    def _init_hx_weight_(self, dout, pd_sck, gain, byte_format, bit_format, reference_unit, offset):
        """
        For initializing the weight sensor.
        :param dout:
        :param pd_sck:
        :param gain:
        :param byte_format:
        :param bit_format:
        :param reference_unit:
        :param offset:
        :return:
        """
        self.hx_weight = HX711(dout, pd_sck, gain, offset=offset)
        self.hx_weight.set_reading_format(byte_format=byte_format, bit_format=bit_format)
        self.hx_weight.set_reference_unit(reference_unit=reference_unit)
        self.hx_weight.reset()
        self.hx_weight.tare()

    def get_weight_translation(self):
        """
        Reads translation data from csv. Translation data is used for converting measured weight to the corresponding
        weight on the machine.
        """
        directory = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + \
                    '/Configuration/weight_translation.csv'
        return pd.read_csv(directory, header=None)

    def _init_vl530_distance_(self, address, TCA9548A_Num, TCA9548A_Addr, mode):
        """
        For initializing the distance sensor.
        :param address:
        :param TCA9548A_Num:
        :param TCA9548A_Addr:
        :param mode:
        :return:
        """
        from VL53L0X_rasp_python.python.VL53L0X import VL53L0X as VL5
        if mode == "VL53L0X_GOOD_ACCURACY_MODE":
            ranging_mode = 0
        elif mode == "VL53L0X_BETTER_ACCURACY_MODE":
            ranging_mode = 1
        elif mode == "VL53L0X_BEST_ACCURACY_MODE":
            ranging_mode = 2
        elif mode == "VL53L0X_LONG_RANGE_MODE":
            ranging_mode = 3
        elif mode == "VL53L0X_HIGH_SPEED_MODE":
            ranging_mode = 4
        else:
            self.logger.info("Inserted ranging mode not valid. Continue with default VL53L0X_LONG_RANGE_MODE")
            ranging_mode = 3
        # self.tof = VL5(address=address, TCA9548A_Num=TCA9548A_Num, TCA9548A_Addr=TCA9548A_Addr)
        # If there are errors with the Distance Sensor, uncomment the next line:
        self.tof = VL5()
        # Start ranging
        self.tof.start_ranging(ranging_mode)
        return ranging_mode

    def get_repetitions(self):
        """
        Returns the current count of repetitions.
        """
        return self._rep_

    def _measure_weight_(self, reps=None):
        """
        Returns the current weight measured.
        """
        if (not self.use_sensors) and (reps is not None):
            with open(self._weights_file_) as weights:
                lines = weights.readlines()
                weight = lines[reps-1].split(",")[1].split("\n")[0]
                print("Weight-File: " + str(weight))
        elif self.use_sensors:
            weight = self.hx_weight.get_weight(5)
            if self.print_weight:
                print("Weightsensor: " + str(weight))
        else:
            weight = 10
        weight = float(weight)
        # round to closest value in weight translation if available
        if self.weight_translation is not None:
            weights = list(self.weight_translation.iloc[:, 1])
            stack_weights = list(self.weight_translation.iloc[:, 0])
            weight = stack_weights[min(range(len(weights)), key=lambda x: abs(weights[x]-weight))]
        self.set_weight(weight)
        return weight

    def set_weight(self, weight):
        if weight >= 0:
            self._weight_ = weight

    def get_last_weight(self):
        return self._weight_

    def is_timed_out(self):
        return self._stop_

    def _check_reps_(self, repetitions, distance_buffer, total_distances):
        """
        Gets distance from distance sensor. Checks whether new repetition has been made. Updates the passed repetitions
        parameter and the distance buffer. Distance buffer contains all distances since the last repetition.
        :param repetitions: Current count of repetitions to be updated.
        :param distance_buffer: Current collection of measured distances to be updated
        :return: [updated repetitions, updated distance_buffer]
        """
        # get current distance. If testing, use distance.csv, otherwise data from sensor
        if not self.use_sensors:
            with open(self._numbers_file_) as numbers:
                lines = numbers.readlines()
                length = len(lines)
                distance = lines[self._no_].split(",")[1]
            self._no_ += 1
            if self._no_ >= length:
                self._stop_ = True
        else:
            distance = self.tof.get_distance()
        if self.print_distance:
            print("Distance: %s" % distance)
        distance = int(distance)
        if self._min_ <= distance <= self._max_:
            # update distance buffer
            distance_buffer += [int(distance)]
            # calculate repetitions and update repetitions-value
            new_reps = repetitions + self._analyze_distance_buffer_(distance_buffer)
        else:
            print("Invalid distance value: %s" % distance)
            new_reps = repetitions
        # empty distance_buffer to save memory
        if new_reps > repetitions:
            total_distances = total_distances + distance_buffer
            distance_buffer = list()
        return new_reps, distance_buffer, total_distances

    def _analyze_distance_buffer_(self, distance_buffer):
        """
        Counts the number of repetitions in a distance buffer. Simple logic that has to be replaced: Counts if a
         distance is smaller than the min-Value. Then waits until half of the distance between min and max has been
         reached again.
        :return: Number of repetitions in the buffer.
        """
        under_max = (distance_buffer[0] < (self._min_ * (2 - self.rep_val)))
        reps = 0
        reps_i = []
        distance_buffer = self._running_mean_(distance_buffer, 10)
        for i in range(0, len(distance_buffer) - 1):
            if under_max:
                if distance_buffer[i] > (self._max_ * self.rep_val):
                    reps += 1
                    reps_i += [i]
                    under_max = False
            elif distance_buffer[i] < (self._min_ * (2 - self.rep_val)):
                under_max = True
        if self.print_undermax:
            print('Undermax: %s' %under_max)
        return reps

    def _reset_timer_(self):
        self.time_out_time = datetime.now() + dt.timedelta(seconds=self.timeout_delta)

    def get_durations(self):
        return self._durations_

    @staticmethod
    def _running_mean_(x, n):
        return np.convolve(x, np.ones((n,)) / n)[(n - 1):]

    @staticmethod
    def _update_durations_starttime_(durations, start_time):
        """
        Updates the durations of the repetitions.
        """
        durations = durations + [(datetime.now() - start_time).total_seconds()]
        return durations, datetime.now()

    def _reset_(self):
        """
        Resets all values created during one recording session.
        """
        self._rep_ = 0
        self._distance_buffer_ = []
        self._total_distances_ = []
        self._weight_list_ = []
        self._durations_ = []
        self.time_out_time = datetime.now() + dt.timedelta(seconds=self.timeout_delta)
        self._stop_ = False
        self._no_ = 0
        self._start_time_ = datetime.now()

    def quit(self):
        if self.use_sensors:
            self.tof.stop_ranging()
            GPIO.cleanup()

    def start_recording(self, set_id, rfid_tag):
        """
        While running, the values of the distance sensor are analyzed. If a new repetition is identified, the current
        value of the weight sensor is taken and a new repetition-request is sent to the server.
        """
        self._reset_()

        self.logger.info("Start recording.")

        fig = None

        if self.plot:
            fig = plt.figure()
            plt.ion()
            plt_line_max = [[0, self.plot_len], [self._max_ * self.rep_val, self._max_ * self.rep_val]]
            plt_line_min = [[0, self.plot_len], [self._min_ * (2 - self.rep_val), self._min_ * (2 - self.rep_val)]]
        while not self._stop_:
            plt.pause(self.frequency)
            # update repetitions
            old_rep = self._rep_
            self._rep_, self._distance_buffer_, self._total_distances_ = self._check_reps_(self._rep_, self._distance_buffer_, self._total_distances_)
            # if new repetition, update all other values
            if old_rep != self._rep_:
                print(self._rep_)
                self._reset_timer_()
                # update durations
                self._durations_, self._start_time_ = self._update_durations_starttime_(self._durations_,
                                                                                        self._start_time_)
                # send update
                self.queue.put_update(repetitions=self._rep_, weight=self._measure_weight_(self._rep_),
                                                set_id=set_id, rfid=rfid_tag, active=True, durations=self._durations_, end=False)
                self._weight_list_ = self._weight_list_ + [self._weight_]
            if self.time_out_time < datetime.now():
                self._stop_ = True
                break

            if self.plot:
                fig.clear()
                plt.plot(plt_line_max[0], plt_line_max[1])
                plt.plot(plt_line_min[0], plt_line_min[1])
                plt.plot((self.plot_len - len(self._distance_buffer_)) * [self._min_] + self._distance_buffer_[-self.plot_len:])
                plt.draw()

        if self.plot:
            plt.close()

        if self.final_plot and not self.plot:
            self._total_distances_ = self._total_distances_ + self._distance_buffer_
            plt_line_max = [[0, len(self._total_distances_)], [self._max_ * self.rep_val, self._max_ * self.rep_val]]
            plt_line_min = [[0, len(self._total_distances_)], [self._min_ * (2 - self.rep_val), self._min_ * (2 - self.rep_val)]]
            plt.plot(plt_line_max[0], plt_line_max[1])
            plt.plot(plt_line_min[0], plt_line_min[1])
            plt.plot((self.plot_len - len(self._total_distances_)) * [self._min_] + self._total_distances_)
            plt.tight_layout()
            plt.show()

        print("Final: rep: " + str(self._rep_) + " Durations: " + str(self._durations_))
        print("Final: rep: " + str(self._rep_) + " Weights: " + str(self._weight_list_))
        self.logger.info('Stop recording.')
