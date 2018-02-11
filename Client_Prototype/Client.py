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
        self.list_address = "https://app-smartgym.herokuapp.com/tracker/set_list_rest/"
        # list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
        self.detail_address = "https://app-smartgym.herokuapp.com/tracker/set_detail_rest/"
        # detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"

        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
        self.request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id)
        self.repetition_manager = RepetitionManager(self)

    """def run(self):
        
        Runs the client.
        
        self.cache.empty_cache()
        while self.is_ready():
            # wait for valid rfid-tag input
            rfid_tag = input('RFID: ')

            # start recording if rfid-tag is valid
            if len(rfid_tag) == 10:
                rep_count = 0
                ex_weight = 0
                # create new set
                response = json.loads(self.new_set(rfid=rfid_tag).decode("utf-8"))
                set_id = response['id']

                # receive repetitions
                while True:
                    rep = input("r for repetition:  ")
                    if rep == "r":
                        rep_count += 1
                        # update set and weight for the first repetition
                        if rep_count == 1:
                            ex_weight = random.randint(5, 100)
                            self.update_set(repetitions=rep_count, weight=ex_weight, set_id=set_id,  rfid=rfid_tag, active=True)
                        # update set keep weight for the next repetitions after the first one
                        else:
                            self.update_set(repetitions=rep_count, weight=ex_weight, set_id=set_id, rfid=rfid_tag, active=True)
                    else:
                        # deactivate current set
                        self.update_set(repetitions=rep_count, weight=ex_weight, set_id=set_id, rfid=rfid_tag, active=False)
                        break
            else:
                print("Not a valid rfid-tag.")
            print()
    """

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

