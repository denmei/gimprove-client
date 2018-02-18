import requests
from datetime import datetime
import os
import pandas as pd
import json
import random
import traceback


class RequestManager:
    """
    Caches messages that could not be sent to the server. Manages duplicates and the sequence of the messages.
    """

    def __init__(self, detail_address, list_address, exercise_name, equipment_id, cache_path):
        self.detail_address = detail_address
        self.list_address = list_address
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
        self.path = cache_path
        self.cache_path = os.path.join(cache_path, "client_cache.txt")
        self._check_cache_file_()

    def rfid_is_valid(self, rfid):
        #TODO
        return True

    def _check_cache_file_(self):
        """
        Checks whether there is a cache_file in the specified directory. If not, a new file will be created.
        """
        if not os.path.isfile(self.cache_path):
            cache_file = open(self.cache_path, 'w')
            cache_file.write("Method | Address | Data | Status Code \n")
            cache_file.close()

    def update_set(self, repetitions, weight, set_id, rfid, active):
        """
        Update an existing set.
        :param repetitions: Repetitions count.
        :param weight: Weight used.
        :param set_id: ID of the set to update.
        :param rfid: RFID of the User.
        :param active: Specify whether set shall stay active or not.
        :return: Server response.
        """
        address = self.detail_address + set_id
        durations = random.sample(range(1, 20), repetitions)
        data = {'repetitions': repetitions, 'weight': weight, 'exercise_name': self.exercise_name,
                'equipment_id': self.equipment_id, 'date_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                'rfid': rfid, 'active': str(active), 'durations': json.dumps(durations)}
        response = requests.put(address, data=data)
        if response.status_code != 200 and response.status_code != 201:
            self.cache_request("update", address, data, str(response.status_code))
        return response

    def new_set(self, rfid, exercise_unit=""):
        """
        Sends a request to create a new set.
        :param rfid: User-RFID
        :param exercise_unit: ID of exercise_unit the set belongs to (if not available: "")
        :return: Server response
        """
        data = {'exercise_unit': exercise_unit, 'repetitions': 0, 'weight': 0, 'exercise_name': self.exercise_name,
                'rfid': rfid, 'date_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                'equipment_id': self.equipment_id, 'active': 'True', 'durations': json.dumps([])}
        response = requests.post(self.list_address, data=data)
        if response.status_code != 200 and response.status_code != 201:
            self.cache_request("new", self.list_address, data, str(response.status_code))
        return response

    def delete_set(self, set_id):
        """
        Sends a request to delete the set with the specified set_id.
        """
        address = self.detail_address + set_id
        response = requests.delete(address)
        if response.status_code != 200 and response.status_code != 201:
            self.cache_request("delete", address, "", str(response.status_code))
        return response

    def cache_request(self, method, address, data, status_code):
        """
        Caches a request if there is a connection/server error. Delete all prior cached messages that belong to the same
        set.
        """
        if status_code[0] == "5" or status_code[0] == "4":
            with open(self.cache_path, "a") as cache_file:
                cache_file.write(str(method) + "|" + str(address) + "|" + str(data) + "|" + status_code + "\n")
                cache_file.close()
            return True
        else:
            return False

    def empty_cache(self):
        """
        Tries to send all cached exercises to the server. And deletes the messages.
        Attention: If requests fails, the request is written back to the cache -> not try again in the same session!
        :return: True if no error occured, else false.
        """
        cache_df = pd.read_table(self.cache_path, sep="|", index_col=False).reindex()
        os.rename(self.cache_path, self.path + "buffer_cache.txt")
        self._check_cache_file_()
        # send messages:
        try:
            for index, row in cache_df.iterrows():
                response = None
                method = row.iloc[0]
                address = row.iloc[1]
                data = json.loads(row.iloc[2].replace("'", '"'))
                if method == 'update':
                    self.update_set(repetitions=data['repetitions'], weight=data['weight'],
                                    set_id=str(address.rsplit("/", 1))[1], rfid=data['rfid'], active=data['active'])
                elif method == 'new':
                    self.new_set(rfid=data['rfid'], exercise_unit=data['exercise_unit'])
                elif method == 'delete':
                    self.delete_set(data['id'])
                # if request was not successfull, try to cache it again
                if response is not None:
                    status_code = response.status_code
                    self.cache_request(method, address, data, status_code)
            os.remove(self.path + "buffer_cache.txt")
            return True
        except Exception as e:
            print("Exception RequestManager: " + str(e))
            print(traceback.print_exc())
            # if an error occurs, recreate the cache and delete the buffer
            os.remove(self.cache_path)
            os.rename(self.path + "buffer_cache.txt", self.cache_path)
            return False
