import logging
from hx711py.hx711 import HX711
import os

import pandas as pd


class WeightSensor:

    def __init(self, config_path, dout, pd_sck, gain, byte_format, bit_format, reference_unit, offset, use_sensors,
               weight_path, print_weight):
        self.config_path = config_path
        self.logger = logging.getLogger('gimprove' + __name__)
        self.use_sensors = use_sensors
        self.print_weight = print_weight

        # init hx711
        self.hx_weight = HX711(dout, pd_sck, gain, offset=offset)
        self.hx_weight.set_reading_format(byte_format=byte_format, bit_format=bit_format)
        self.hx_weight.set_reference_unit(reference_unit=reference_unit)
        self.hx_weight.reset()
        self.hx_weight.tare()

        # get translation table
        self.translation_table = pd.read_csv(os.path.join(config_path, 'weight_translation.csv'), header=None)

        # get fake weights
        self.fake_weights = pd.read_csv(os.path.join(weight_path, ""), header=None)

    def get_current_weight(self, reps=None):
        """
        Returns the current weight measured.
        """
        if (not self.use_sensors) and (reps is not None):
            with open(self._weights_file_) as weights:
                lines = weights.readlines()
                pre_weight = lines[reps-1].split(",")[1].split("\n")[0]
                print("Weight-File: " + str(weight))
        elif self.use_sensors:
            pre_weight = self.hx_weight.get_weight(5)
        else:
            pre_weight = 10
        pre_weight = float(pre_weight)
        # round to closest value in weight translation if available
        weights = list(self.translation_table.iloc[:, 1])
        stack_weights = list(self.translation_table.iloc[:, 0])
        weight = stack_weights[min(range(len(weights)), key=lambda x: abs(weights[x]-pre_weight))]
        if self.print_weight:
            print("Original weight: %s, translated weight: %s" %(pre_weight, weight))
        return weight


