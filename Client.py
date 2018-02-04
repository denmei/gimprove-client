import requests
import json
from hx711py.hx711 import HX711
import random
import time
from datetime import datetime

# TODO cache requests that failed because of a connection error


class Equipment(HX711):

    # list_address = "https://app-smartgym.herokuapp.com/tracker/set_list_rest/"
    list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
    # detail_address = "https://app-smartgym.herokuapp.com/tracker/set_detail_rest/"
    detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"

    def __init__(self, exercise_name, equipment_id):
        super(Equipment, self).__init__(5, 6)
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id

    def new_set(self, repetitions, weight, rfid, exercise_unit=""):
        data = {'exercise_unit': exercise_unit, 'repetitions': repetitions,
                   'weight': weight, 'exercise_name': self.exercise_name, 'rfid': rfid,
                   'date_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'equipment_id':self.equipment_id, 'active': 'True'}
        r = requests.post(self.list_address, data=data, )
        print(r.status_code)
        print(r.content)
        return r.content

    def get_sets(self):
        r = requests.get(self.list_address)
        print(json.dumps(r.json(), sort_keys=True, indent=3))

    def update_set(self, repetitions, weight, set_id, rfid, active, exercise_unit=""):
        address = self.detail_address + set_id
        r = requests.put(address, data={'repetitions': repetitions, 'weight': weight,
                                        'exercise_name': self.exercise_name, 'equipment_id':self.equipment_id,
                                        'date_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), 'rfid': rfid,
                                        'active': str(active)})
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
                print("Receiving repetitions")
                rep_count = 0
                set_id = ""
                ex_weight = 0
                while rep_count < 10:
                    # create new set
                    if rep_count == 0:
                        response = json.loads(self.new_set(weight=0, repetitions=rep_count, rfid=rfid_tag).decode("utf-8"))
                        set_id = response['id']
                    # update set and weight
                    elif rep_count == 1:
                        ex_weight = random.randint(5, 100)
                        self.update_set(repetitions=rep_count, weight=ex_weight, set_id=set_id,  rfid=rfid_tag, active=True)
                    # update set keep weight
                    else:
                        self.update_set(repetitions=rep_count, weight=ex_weight, set_id=set_id, rfid=rfid_tag, active=True)
                    rep_count += 1
                    time.sleep(1)
                self.update_set(repetitions=rep_count, weight=ex_weight, set_id=set_id, rfid=rfid_tag, active=False)
            else:
                print("Not a valid rfid-tag.")
            print()

equipment = Equipment(exercise_name='Lat Pulldown', equipment_id="1b7d032196154bd5a64c7fcfee388ec5")
equipment.run()
