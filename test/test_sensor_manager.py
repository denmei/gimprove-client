import unittest
from Client_Prototype.SensorManager import SensorManager
from Client_Prototype.RequestManager import RequestManager
import json
import random
import logging
from pathlib import Path
import os


class TestSensorManager(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
        self.detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"
        self.user_profile_rfid_address = "http://127.0.0.1:8000/tracker/userprofile_detail_rfid_rest/"
        self.user_profile_address = "http://127.0.0.1:8000/tracker/userprofile_detail_rest/"
        self.exercise_name = 'Lat Pulldown'
        self.equipment_id = "653c9ed38b004f52bbc83fba95dc81cf"
        self.cache_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + "/Configuration"
        self.cache_file_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + \
                               "/Configuration/client_cache.txt"
        self.rfid = "0006921147"

        request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path=self.cache_path,
                                              userprofile_detail_address=self.user_profile_rfid_address)
        self.sensor_manager = SensorManager(
            request_manager=request_manager,
            min_dist=470,
            max_dist=900,
            use_sensors=False,
            print_weight=False,
            print_distance=False,
            print_undermax=False,
            final_plot=False,
            distances_file=str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/distances_short.csv',
            weights_file=str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/weights.csv'
        )

    def test_distance_validation(self):
        """
        Tests validation of distance measurements. Distances outside of the predefined range must be ignored.
        """
        # test invalid measurement
        reps, buffer = self.sensor_manager._check_reps_(0, [])
        self.assertEqual(reps, 0)
        self.assertEqual(len(buffer), 0)
        # test valid measurement
        reps, buffer = self.sensor_manager._check_reps_(0, [])
        self.assertEqual(len(buffer), 1)

    def test_repetition_detection(self):
        """
        Tests whether all repetitions in a file are detected.
        """
        distance_buffer = []
        repetitions = 0
        with open(str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/distances_long.csv') as numbers:
            lines = numbers.readlines()
            length = len(lines)
        print(length)
        self.sensor_manager._numbers_file_ = str(
            Path(os.path.dirname(os.path.realpath(__file__)))) + '/distances_long.csv'
        for x in range(0, length):
            repetitions, distance_buffer = self.sensor_manager._check_reps_(repetitions, distance_buffer)
        self.assertEqual(repetitions, 10)
        self.sensor_manager._numbers_file_ = str(
            Path(os.path.dirname(os.path.realpath(__file__)))) + '/distances_short.csv'
