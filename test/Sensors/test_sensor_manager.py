import unittest
from Client_Prototype.Sensors.SensorManager import SensorManager
from Client_Prototype.Communication.MessageQueue import MessageQueue
import logging
from pathlib import Path
import os


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

        print(str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_short.csv')

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
            weights_file=str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_short.csv'
        )

    def test_distance_validation(self):
        """
        Tests validation of distance measurements. Distances outside of the predefined range must be ignored.
        """
        # test invalid measurement
        reps, buffer, total = self.sensor_manager._check_reps_(0, [], list())
        self.assertEqual(reps, 0)
        self.assertEqual(len(buffer), 0)
        # test valid measurement
        reps, buffer, total = self.sensor_manager._check_reps_(0, [], list())
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
        self.sensor_manager._numbers_file_ = \
            str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_long.csv'
        for x in range(0, length):
            repetitions, distance_buffer, total = self.sensor_manager._check_reps_(repetitions, distance_buffer, total)
        self.assertEqual(repetitions, 10)
        self.sensor_manager._numbers_file_ = \
            str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_long.csv'