import json
from Client_Prototype.RequestManager import RequestManager
from Client_Prototype.SensorManager import SensorManager
from Client_Prototype.Timer import Timer
import time


class Equipment:
    """
    Represents a component to upgrade a gym machine. Can record new exercise units and send the results to the
    SmartGym-Server.
    In case of a connection error, the results will be cached an resent at another point of time.
    """

    def __init__(self, exercise_name, equipment_id):
        # self.list_address = "https://app-smartgym.herokuapp.com/tracker/set_list_rest/"
        self.list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
        # self.detail_address = "https://app-smartgym.herokuapp.com/tracker/set_detail_rest/"
        self.detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"

        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
        self.request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id)

    def _init_set_record_(self, rfid):
        """
        Creates a new set with repetitions = 0 and weight = 0. Returns server response including the set id.
        :param rfid:
        :return:
        """
        # create set
        # TODO: exercise unit check
        response = json.loads(self.request_manager.new_set(rfid, "").content.decode("utf-8"))
        print("init ok")
        return response

    def _end_set_(self, rfid_tag, set_id, repetitions, weight):
        """
        Deactivates the specified set.
        :param rfid_tag:
        :param set_id:
        :param repetitions:
        :param weight:
        :return:
        """
        self.request_manager.update_set(rfid=rfid_tag, set_id=set_id, active=False, repetitions=repetitions,
                                        weight=weight)

    def run(self):
        while True:
            # start waiting for rfid tag
            rfid_tag = input('RFID (0006921147):')
            # check validity of rfid tag.
            if self.request_manager.rfid_is_valid(rfid_tag):
                # init set
                set_id = self._init_set_record_(rfid_tag)['id']
                timer = Timer(8)
                # start sensor thread
                sensor_manager = SensorManager(rfid_tag=rfid_tag, set_id=set_id, timer=timer)
                sensor_manager.start()
                # start timer
                timer.start()
                # while not time out nor sensor manager ready, do nothing
                while not timer.is_timed_out() or False:
                    pass
                # stop subthreads
                print("stopped")
            else:
                # print error
                print("Not a valid rfid tag")


equipment = Equipment(exercise_name='Lat Pulldown', equipment_id="1b7d032196154bd5a64c7fcfee388ec5")
equipment.run()

