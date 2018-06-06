import unittest
from Client_Prototype.Sensors.WeightSensor import WeightSensor
import logging
from pathlib import Path
import os
import pandas as pd


class TestSensorManager(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        weight_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/weights.csv'
        translation_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + '/test_data/weight_translation.csv'
        self.weight_sensor = WeightSensor( dout=5, pd_sck=6, gain=128, byte_format="LSB", bit_format="MSB",
                                           reference_unit=92, offset="", use_sensors=False, weight_path=weight_path,
                                           print_weight=True, translation_path=translation_path)

    def test_weight_retrieval_reps(self):
        """
        Tests whether weights are read and translated correctly.
        """
        weight_1 = self.weight_sensor.get_current_weight(reps=0)
        self.assertEqual(weight_1, 9.4)
        weight_2 = self.weight_sensor.get_current_weight(reps=1)
        self.assertEqual(weight_2, 14.6)
