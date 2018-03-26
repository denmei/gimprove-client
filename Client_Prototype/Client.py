import json
from Client_Prototype.RequestManager import RequestManager
from Client_Prototype.SensorManager import SensorManager
import traceback
import logging
import os
from pathlib import Path
from datetime import datetime


class Equipment:
    """
    Represents a component to upgrade a gym machine. Can record new exercise units and send the results to the
    SmartGym-Server.
    In case of a connection error, the results will be cached an resent at another point of time.
    """

    def __init__(self, testing=True):
        """
        :param testing: If true, runs in test mode (APIs of the test-environment). Else, production environment is used.
        """
        self.testing = testing
        self.config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + "/Configuration/"
        self._configure_()
        self._configure_logger_()
        self.list_address, self.detail_address, self.userprofile_detail_address = self._load_links_(testing)
        self.request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path=self.config_path,
                                              userprofile_detail_address=self.userprofile_detail_address)
        self.sensor_manager = self._initialize_sensormanager_(self.config_path + "/config.json", self.request_manager,
                                                              self.testing)
        self.logger.info("Client instantiated.")
        if not testing:
            self.logger.warning("Running on production environment.")

    def _configure_(self):
        """
        Configures the attributes of the equipment class from the configuration file.
        """
        with open(self.config_path + "/config.json") as config_file:
            configuration = json.load(config_file)
        self.exercise_name = configuration['exercise_name']
        self.equipment_id = configuration['equipment_id']

    def _configure_logger_(self):
        """
        Configures and instantiates the logger.
        """
        # check whether log-directory exists:
        if "logs" not in os.listdir(self.config_path):
            os.mkdir(self.config_path + "/logs")

        # check whether logging file exists:
        log_name = "logging" + str(datetime.now().date()) + ".log"
        if log_name not in os.listdir(self.config_path + "/logs"):
            logging_file = open(self.config_path + "/logs/" + log_name, 'w')
            logging_file.close()

        logging.basicConfig(
            filename=self.config_path + "/logs/" + log_name,
            format="%(name)s %(levelname) - 10s %(asctime)s %(funcName)s %(message)s",
            level=logging.INFO
        )
        self.logger = logging.getLogger('gimprove' + __name__)
        logging.getLogger("requests").setLevel(logging.WARNING)

    def _load_links_(self, testing=True):
        """
        Loads the links for the APIs of the GImprove-Server.
        :param testing: If true, the APIs of the testing environment are loaded. Else production environment.
        :return [link set_list, link to set_detail, link to userprofile_detail(rfid)]
        """
        with open(self.config_path + "/api-links.json") as links_file:
            if not testing:
                links = json.load(links_file)['links']['production-links']
            else:
                links = json.load(links_file)['links']['testing-links']
        links_file.close()
        return links['set_list']['link'], links['set_detail']['link'], links['userprofile_detail']['link']

    @staticmethod
    def _initialize_sensormanager_(config_file_path, request_manager, testing):
        """
        Creates a sensor manager-instance with the settings specified in the config_file.
        :return SensorManager-Instance
        """
        with open(config_file_path) as config_file:
            settings = json.load(config_file)
        config_file.close()
        plot_settings = settings['plot_settings']
        distance_settings = settings['sensor_settings']['distance_sensor']
        weight_settings = settings['sensor_settings']['weight_sensor']
        sensor_manager = SensorManager(request_manager=request_manager,
                                       min_dist=distance_settings['min_dist'],
                                       max_dist=distance_settings['max_dist'],
                                       dout=weight_settings['dout'],
                                       pd_sck=weight_settings['pd_sck'],
                                       gain=weight_settings['gain'],
                                       byte_format=weight_settings['byte_format'],
                                       bit_format=weight_settings['bit_format'],
                                       reference_unit=weight_settings['reference_unit'],
                                       testing=testing, plot_len=plot_settings['length'],
                                       frequency=distance_settings['frequency'],
                                       rep_val=distance_settings['rep_val'],
                                       timeout_delta=distance_settings['timeout_delta'],
                                       address=hex(distance_settings['address']),
                                       TCA9548A_Num=distance_settings['TCA9548A_Num'],
                                       TCA9548A_Addr=distance_settings['TCA9548A_Addr'],
                                       ranging_mode=distance_settings['ranging_mode'])
        print(hex(distance_settings['address']))
        return sensor_manager

    def _init_set_record_(self, rfid):
        """
        Creates a new set with repetitions = 0 and weight = 0. Returns server response including the set id.
        :return: server response
        """
        # create set
        response = json.loads(self.request_manager.new_set(rfid, "").content.decode("utf-8"))
        return response

    def _end_set_(self, rfid_tag, set_id, repetitions, weight, durations):
        """
        Deactivates the specified set.
        :return: server response
        """
        return self.request_manager.update_set(rfid=rfid_tag, set_id=set_id, active=False, repetitions=repetitions,
                                               weight=weight, durations=durations)

    def _delete_set_(self, set_id):
        """
        Sends a request to delete the specified set.
        :return: server response
        """
        return self.request_manager.delete_set(set_id=set_id)

    def run(self):
        """
        Runs the whole application.

        When started, the application waits for a RFID-Tag as input. If the input passes the validation, a new set is
        created by sending a corresponding request to the server. After that, a new Thread is started to record the
        current set-session. Furthermore, a timer is started to stop the recording in case of inactivity. Once the
        recording is finished, a new request to the server deactivates the current set.

        If there occurs an error, the new set is deleted by sending a request to the server.
        """
        while True:
            # start waiting for rfid tag
            rfid_tag = input('RFID (0006921147):')
            self.logger.info("RFID-read: " + rfid_tag)
            # check validity of rfid tag.
            set_id = None
            if self.request_manager.rfid_is_valid(rfid_tag):
                try:
                    # init set
                    set_id = self._init_set_record_(rfid_tag)['id']
                    # start sensor thread
                    self.sensor_manager.start_recording(rfid_tag=rfid_tag, set_id=set_id)
                    # end set
                    self._end_set_(rfid_tag=rfid_tag, set_id=set_id, repetitions=self.sensor_manager.get_repetitions(),
                                   weight=self.sensor_manager.get_weight(), durations=self.sensor_manager.get_durations())

                except Exception as e:
                    print(traceback.print_exc())
                    if set_id is not None:
                        self._delete_set_(set_id)
            else:
                self.logger.info("RFID-tag not valid: " + rfid_tag)
                print("Not a valid rfid tag")

if __name__ == '__main__':
    equipment = Equipment(testing=True)
    equipment.run()



