import requests
import json
from hx711py.hx711 import HX711
import random
import time

# TODO cache requests that failed because of a connection error


class Equipment(HX711):

    list_address = "https://app-smartgym.herokuapp.com/tracker/set_list_rest/"
    detail_address = "https://app-smartgym.herokuapp.com/tracker/set_detail_rest/"

    def __init__(self, exercise_name, equipment_id):
        super(Equipment, self).__init__(5, 6)
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id

    def new_set(self, repetitions, weight, rfid, exercise_unit=""):
        r = requests.post(self.list_address, data={'exercise_unit': exercise_unit, 'repetitions': repetitions,
                                                   'weight': weight, 'exercise_name': self.exercise_name, 'rfid': rfid})
        print(r.status_code)

    def get_sets(self):
        r = requests.get(self.list_address)
        print(json.dumps(r.json(), sort_keys=True, indent=3))

    def update_set(self, repetitions, weight, set_id, exercise_unit=""):
        address = self.detail_address + set_id
        r = requests.put(address, data={'exercise_unit': exercise_unit, 'repetitions': repetitions, 'weight': weight,
                                        'exercise_name': self.exercise_name})
        print(r.status_code)

    def delete_set(self, set_id):
        address = self.detail_address + set_id
        r = requests.delete(address)
        print(r.status_code)

    def _cache_exercise_(self):
        """
        Caches an exercise if there is a connection error.
        :return:
        """
        pass

    def _empty_cache_(self):
        """
        Tries to send all cached exercises to the server. Date values have to be updated then!
        :return:
        """
        pass

    def run(self):
        self._empty_cache_()
        while self.is_ready():
            # wait for valid rfid-tag input
            rfid_tag = input('RFID: ')
            if len(rfid_tag) == 10:
                print("  Waiting for input")
                # get repetition and weight input
                ex_weight = random.randint(5, 100)
                ex_repetitions = random.randint(5, 15)
                # send to client
                self.new_set(weight=ex_weight, repetitions=ex_repetitions, rfid=rfid_tag)
            else:
                print("Not a valid rfid-tag.")
            print()

equipment = Equipment(exercise_name='Lat Pulldown', equipment_id="123456789")
equipment.run()
