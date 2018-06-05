import unittest
from Client_Prototype.Sensors.DistanceSensor import DistanceSensor
import logging
from pathlib import Path
import os


class TestDistanceSensor(unittest.TestCase):
    """
    Tests DistanceSensor-Module in non-sensor-mode.
    """

    def setUp(self):
        distance_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/distances_long.csv'
        self.distance_sensor = DistanceSensor(address=0x29, TCA9548A_Num=255, TCA9548A_Addr=0,
                                              mode="VL53L0X_BETTER_ACCURACY_MODE", fake_distances_path=distance_path,
                                              use_sensors=False, print_distance=False)

    def test_get_distance(self):
        """
        DistanceSensor must return the correct distances from csv-file.
        :return:
        """
        distance = self.distance_sensor.get_distance()
        self.assertEqual(distance, 478)
        distance = self.distance_sensor.get_distance()
        self.assertEqual(distance, 479)

    def test_reset_sensor(self):
        """
        After the reset, the distance sensor must return the first value of the csv-file.
        :return:
        """
        distance_1 = self.distance_sensor.get_distance()
        self.distance_sensor.reset_distance_sensor()
        distance_2 = self.distance_sensor.get_distance()
        self.assertEqual(distance_1, distance_2)
