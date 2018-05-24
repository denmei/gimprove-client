import json
from Client_Prototype.Communication.RequestManager import RequestManager
from Client_Prototype.Sensors.SensorManager import SensorManager
import traceback
import logging
import os
from pathlib import Path
from datetime import datetime
from Client_Prototype.Communication.s3Manager import s3Manager
from Client_Prototype.Communication.MessageQueue import MessageQueue
from Client_Prototype.Helpers.Configurator import Configurator


class Equipment:
    """
    Represents a component to upgrade a gym machine. Can record new exercise units and send the results to the
    SmartGym-Server.
    In case of a connection error, the results will be cached an resent at another point of time.
    """

    def __init__(self, environment=None):
        self.config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + "/Configuration/"
        self._configure_()
        self.logger = logging.getLogger('gimprove' + __name__)
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.configurator = Configurator(self.config_path, "config.json", environment=environment)
        self.list_address, self.detail_address, self.userprofile_detail_address, self.websocket_address, token_address \
            = self.configurator.get_api_links()
        self.message_queue = MessageQueue()
        self.request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path=self.config_path,
                                              userprofile_detail_address=self.userprofile_detail_address,
                                              token_address=token_address,
                                              websocket_address=self.websocket_address, message_queue=self.message_queue,
                                              password=self.password, token=None)
        self.sensor_manager = self._initialize_sensormanager_(self.config_path + "/config.json", self.message_queue)
        self.logger.info("Client instantiated.")
        self._upload_logs_(self.config_path + "/logs", self.equipment_id, self.bucket, self.environment)

    def _configure_(self):
        """
        Configures the attributes of the equipment class from the configuration file.
        """
        with open(self.config_path + "/config.json") as config_file:
            configuration = json.load(config_file)
        self.exercise_name = configuration['exercise_name']
        self.equipment_id = configuration['equipment_id']
        self.environment = configuration['communication']['environment']
        self.bucket = configuration['aws']['bucket']
        self.password = configuration['password']

    @staticmethod
    def _initialize_sensormanager_(config_file_path, message_queue):
        """
        Creates a sensor manager-instance with the settings specified in the config_file.
        :return SensorManager-Instance
        """
        with open(config_file_path) as config_file:
            settings = json.load(config_file)
        config_file.close()
        sensor_settings = settings['sensor_settings']
        plot_settings = settings['plot_settings']
        distance_settings = settings['sensor_settings']['distance_sensor']
        weight_settings = settings['sensor_settings']['weight_sensor']
        terminal_settings = settings['terminal_settings']
        sensor_manager = SensorManager(queue=message_queue,
                                       min_dist=distance_settings['min_dist'],
                                       max_dist=distance_settings['max_dist'],
                                       dout=weight_settings['dout'],
                                       pd_sck=weight_settings['pd_sck'],
                                       gain=weight_settings['gain'],
                                       byte_format=weight_settings['byte_format'],
                                       bit_format=weight_settings['bit_format'],
                                       reference_unit=weight_settings['reference_unit'],
                                       use_sensors=(sensor_settings['use_sensors'] == 'True'),
                                       plot_len=plot_settings['length'],
                                       plot=(plot_settings['plot'] == 'True'),
                                       frequency=distance_settings['frequency'],
                                       rep_val=distance_settings['rep_val'],
                                       timeout_delta=distance_settings['timeout_delta'],
                                       address=hex(distance_settings['address']),
                                       TCA9548A_Num=distance_settings['TCA9548A_Num'],
                                       TCA9548A_Addr=distance_settings['TCA9548A_Addr'],
                                       ranging_mode=distance_settings['ranging_mode'],
                                       print_weight=(terminal_settings['print_weight'] == 'True'),
                                       print_distance=(terminal_settings['print_distance'] == 'True'),
                                       print_undermax=(terminal_settings['print_undermax'] == 'True'),
                                       final_plot=(plot_settings['final_plot'] == 'True'),
                                       weight_translation=weight_settings['weight_translation'] == 'True',
                                       distances_file=str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + '/distances.csv',
                                       weights_file=str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + '/weights.csv')
        return sensor_manager

    def _upload_logs_(self, logging_path, device_id, bucket_name, environment):
        """
        Uploads all available logs before except the one of the current day and deletes them.
        :param logging_path: Path where logs are stored.
        :param device_id:  ID of the client.
        """
        s3_manager = s3Manager(bucket_name, environment)
        for log in os.listdir(logging_path):
            date = datetime.date(datetime.strptime(log.split('logging', 1)[1].split('.log', 1)[0], '%Y-%m-%d'))
            # upload only files of previous days
            if date < date.today():
                try:
                    s3_manager.upload_logs_to_s3(os.path.join(logging_path, log), device_id, log)
                    os.remove(os.path.join(logging_path, log))
                except Exception as e:
                    self.logger.debug(e)
                    break

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
                                               weight=weight, durations=durations, end=True)

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
            rfid_tag = input('RFID (0006921147) or quit:')
            self.logger.info("RFID-read: " + rfid_tag)
            # check validity of rfid tag.
            set_id = None
            if rfid_tag == 'quit':
                self.sensor_manager.quit()
                break
            elif self.request_manager.rfid_is_valid(rfid_tag):
                try:
                    # init set
                    set_id = self._init_set_record_(rfid_tag)['id']
                    # start sensor thread
                    self.sensor_manager.start_recording(rfid_tag=rfid_tag, set_id=set_id)
                    # end set
                    self._end_set_(rfid_tag=rfid_tag, set_id=set_id, repetitions=self.sensor_manager.get_repetitions(),
                                   weight=self.sensor_manager.get_last_weight(), durations=self.sensor_manager.get_durations())

                except Exception as e:
                    print(traceback.print_exc())
                    if set_id is not None:
                        self._delete_set_(set_id)
            else:
                self.logger.info("RFID-tag not valid: " + rfid_tag)
                print("Not a valid rfid tag")


if __name__ == '__main__':
    equipment = Equipment()
    equipment.run()
