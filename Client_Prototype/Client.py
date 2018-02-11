import json
from Client_Prototype.RequestManager import RequestManager
from Client_Prototype.RepetitionManager import RepetitionManager


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
        self.repetition_manager = RepetitionManager(self)

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

    def add_repetition(self, rfid_tag, set_id, repetitions, weight):
        """
        Sends a request to update the repetition count of a set.
        :param rfid_tag:
        :param set_id:
        :param repetitions:
        :param weight:
        :return:
        """
        # TODO: start thread to make the update request
        self.request_manager.update_set(rfid=rfid_tag, set_id=set_id, active=True, repetitions=repetitions,
                                        weight=weight)

    def end_set(self, rfid_tag, set_id, repetitions, weight):
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
                # start recording
                self.repetition_manager.start(set_id=set_id, rfid_tag=rfid_tag)
            else:
                # print error
                print("Not a valid rfid tag")


equipment = Equipment(exercise_name='Lat Pulldown', equipment_id="1b7d032196154bd5a64c7fcfee388ec5")
equipment.run()

