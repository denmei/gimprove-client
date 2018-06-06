import unittest
from Client_Prototype.Sensors.SensorManager import SensorManager
from Client_Prototype.Communication.MessageQueue import MessageQueue
import logging
from pathlib import Path
import os
import pandas as pd


class TestSensorManager(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
        self.websocket_address = "ws://127.0.0.1:8000/ws/tracker/"
        self.detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"
        self.log_address = "http://127.0.0.1:8000/tracker/log_rest/"
        self.exercise_name = 'Lat Pulldown'
        self.equipment_id = "653c9ed38b004f52bbc83fba95dc81cf"
        self.rfid = "0006921147"

        self.sensor_manager = SensorManager(
            queue=MessageQueue(),
            min_dist=470,
            max_dist=900,
            use_sensors=False,
            print_weight=False,
            print_distance=False,
            print_undermax=False,
            final_plot=False,
            distances_file=str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_short.csv',
            weights_file=str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/weights.csv',
            weight_translation=True
        )

    def test_distance_validation(self):
        """
        Tests validation of distance measurements. Distances outside of the predefined range must be ignored.
        """
        # test invalid measurement
        reps, buffer, total = self.sensor_manager._check_reps_(0, [], list())
        self.assertEqual(reps, 0)
        self.assertEqual(len(buffer), 0)
        print(buffer)
        # test valid measurement
        reps, buffer, total = self.sensor_manager._check_reps_(0, [], list())
        print(buffer)
        self.assertEqual(len(buffer), 1)

    def test_repetition_detection(self):
        """
        Tests whether all repetitions in a file are detected.
        """
        distance_buffer = []
        repetitions = 0
        total = []
        with open(str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_long.csv') as numbers:
            lines = numbers.readlines()
            length = len(lines)
        self.sensor_manager.distance_sensor.fake_distances = \
            pd.read_csv(str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_long.csv', header=None)
        for x in range(0, length):
            repetitions, distance_buffer, total = self.sensor_manager._check_reps_(repetitions, distance_buffer, total)
        self.assertEqual(repetitions, 10)
        self.sensor_manager._numbers_file_ = \
            str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_long.csv'

    def test_weight_retrieval_with_translation(self):
        """
        Fake data for weight must be retrieved and translated correctly.
        """
        self.assertEqual(self.sensor_manager.get_last_weight(), 0.0)
        self.assertEqual(self.sensor_manager._measure_weight_(0), 9.4)
        self.assertEqual(self.sensor_manager._measure_weight_(1), 14.6)

    def test_weight_retrieval_no_translation(self):
        """
        Weight-fake data must be retrieved correctly without translation.
        """
        sensor_manager = SensorManager(
            queue=MessageQueue(),
            min_dist=470,
            max_dist=900,
            use_sensors=False,
            print_weight=False,
            print_distance=False,
            print_undermax=False,
            final_plot=False,
            distances_file=str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_short.csv',
            weights_file=str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/weights.csv',
            weight_translation=False
        )
        self.assertEqual(sensor_manager.get_last_weight(), 0.0)
        self.assertEqual(sensor_manager._measure_weight_(0), 10.5)
        self.assertEqual(sensor_manager._measure_weight_(1), 16.2)
        # sensor manager must store the last weight
        self.assertEqual(sensor_manager.get_last_weight(), 16.2)
        print(sensor_manager._weight_list_)

    def test_time_out(self):
        # TODO: SensorManager must time out/stop after predefined period of time.
        pass
