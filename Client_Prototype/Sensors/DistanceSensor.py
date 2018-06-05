import logging
import os
import pandas as pd


class DistanceSensor:
    """
    Interface to the Distance Sensor.
    """

    def __init__(self, address, TCA9548A_Num, TCA9548A_Addr, mode, fake_distances_path, use_sensors, print_distance):
        """
        For initializing the distance sensor.
        :param address:
        :param TCA9548A_Num:
        :param TCA9548A_Addr:
        :param mode:
        :return:
        """
        self.logger = logging.getLogger('gimprove' + __name__)
        self.use_sensors = use_sensors
        self.print_distance = print_distance
        self._no_ = 0
        if mode == "VL53L0X_GOOD_ACCURACY_MODE":
            self.ranging_mode = 0
        elif mode == "VL53L0X_BETTER_ACCURACY_MODE":
            self.ranging_mode = 1
        elif mode == "VL53L0X_BEST_ACCURACY_MODE":
            self.ranging_mode = 2
        elif mode == "VL53L0X_LONG_RANGE_MODE":
            self.ranging_mode = 3
        elif mode == "VL53L0X_HIGH_SPEED_MODE":
            self.ranging_mode = 4
        else:
            self.logger.info("Inserted ranging mode not valid. Continue with default VL53L0X_LONG_RANGE_MODE")
        # load fake distances
        self.fake_distances = pd.read_csv(os.path.join(fake_distances_path, "distances.csv"), header=None)

        if use_sensors:
            from VL53L0X_rasp_python.python.VL53L0X import VL53L0X as VL5
            # If there are errors with the Distance Sensor, uncomment the next line:
            # self.tof = VL5(address=address, TCA9548A_Num=TCA9548A_Num, TCA9548A_Addr=TCA9548A_Addr)
            self.tof = VL5()
            # Start ranging
            self.tof.start_ranging(self.ranging_mode)

    def get_ranging_mode(self):
        return self.ranging_mode

    def get_distance(self):
        if not self.use_sensors:
            distance = int(self.fake_distances[1][self._no_])
            self._no_ += 1
            if self._no_ >= len(self.fake_distances):
                distance = None
        else:
            distance = int(self.tof.get_distance())
        if self.print_distance:
            print("Distance: %s" % distance)
        return distance

    def quit(self):
        self.tof.stop_ranging()

    def reset_distance_sensor(self):
        self._no_ = 0
