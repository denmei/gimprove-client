import json
from Client_Prototype.RequestManager import RequestManager
from Client_Prototype.SensorManager import SensorManager
from Client_Prototype.Timer import Timer
import traceback


class Equipment:
    """
    Represents a component to upgrade a gym machine. Can record new exercise units and send the results to the
    SmartGym-Server.
    In case of a connection error, the results will be cached an resent at another point of time.
    """

    def __init__(self, exercise_name, equipment_id):
        self.list_address = "https://app-smartgym.herokuapp.com/tracker/set_list_rest/"
        # self.list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
        self.detail_address = "https://app-smartgym.herokuapp.com/tracker/set_detail_rest/"
        # self.detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"
        self.userprofile_detail_address = "https://app-smartgym.herokuapp.com/tracker/userprofile_detail_rfid_rest/"
        # self.userprofile_detail_address = "http://127.0.0.1:8000/tracker/userprofile_detail_rfid_rest/"

        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
        self.request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path="/home/dennis/Dokumente/",
                                              userprofile_detail_address=self.userprofile_detail_address)

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
                print("Not a valid rfid tag")

if __name__ == '__main__':
    equipment = Equipment(exercise_name='Lat Pulldown', equipment_id="fded5e7ff5044992bb70949f3aec172c")
    equipment.run()



