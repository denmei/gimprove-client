import json
from Client_Prototype.RequestManager import RequestManager
from Client_Prototype.SensorManager import SensorManager
from Client_Prototype.Timer import Timer
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
        :param config_path: Path to the directory with the configuration files.
        :param testing: If true, runs in test mode (APIs of the test-environment). Else, production environment is used.
        """
        self.config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + "/Configuration"
        self._configure_()
        self._configure_logger_()
        self._load_links_(testing)
        self.request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path="/home/dennis/Dokumente/",
                                              userprofile_detail_address=self.userprofile_detail_address)
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
        if not "logs" in os.listdir(self.config_path):
            os.mkdir(self.config_path + "/logs")

        # check whether logging file exists:
        log_name = "logging" + str(datetime.now().date()) + ".log"
        if not log_name in os.listdir(self.config_path + "/logs"):
            logging_file = open(self.config_path + "/logs/" + log_name, 'w')
            logging_file.close()

        logging.basicConfig(
            filename=self.config_path + "/logs/" + log_name,
            format="%(name)s %(levelname) - 10s %(asctime)s %(funcName)s %(message)s",
            level=logging.INFO
        )
        self.logger = logging.getLogger('gimprove' + __name__)

    def _load_links_(self, testing=True):
        """
        Loads the links for the APIs of the GImprove-Server.
        :param testing: If true, the APIs of the testing environment are loaded. Else production environment.
        """
        with open(self.config_path + "/api-links.json") as links_file:
            if not testing:
                links = json.load(links_file)['production-links']
            else:
                links = json.load(links_file)['testing-links']
        links_file.close()
        self.list_address = links['set_list']['link']
        self.detail_address = links['set_detail']['link']
        self.userprofile_detail_address = links['userprofile_detail']['link']

    def _init_set_record_(self, rfid):
        """
        Creates a new set with repetitions = 0 and weight = 0. Returns server response including the set id.
        :return: server response
        """
        # create set
        # TODO: exercise unit check
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
                    timer = Timer(8)
                    # start sensor thread
                    sensor_manager = SensorManager(rfid_tag=rfid_tag, set_id=set_id, timer=timer,
                                                   request_manager=self.request_manager)
                    sensor_manager.start()
                    # start timer
                    timer.start()
                    # while not time out nor sensor manager ready, do nothing
                    while not timer.is_timed_out() and sensor_manager.is_alive():
                        pass
                    # stop both threads
                    timer.stop_timer()
                    sensor_manager.stop_thread()
                    # end set
                    self._end_set_(rfid_tag=rfid_tag, set_id=set_id, repetitions=sensor_manager.get_repetitions(),
                                   weight=sensor_manager.get_weight(), durations=sensor_manager.get_durations())
                except Exception as e:
                    print(traceback.print_exc())
                    if set_id is not None:
                        # TODO: set inactive
                        self._delete_set_(set_id)
            else:
                self.logger.info("RFID-tag not valid: " + rfid_tag)
                print("Not a valid rfid tag")

if __name__ == '__main__':
    equipment = Equipment(testing=True)
    equipment.run()



