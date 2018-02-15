import requests
from datetime import datetime
import os


class RequestManager:
    """
    Caches messages that could not be sent to the server. Manages duplicates and the sequence of the messages.
    """

    def __init__(self, detail_address, list_address, exercise_name, equipment_id, cache_path):
        self.detail_address = detail_address
        self.list_address = list_address
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
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
            cache_file.write("Method | Address | Data | Status Code")
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
        data = {'repetitions': repetitions, 'weight': weight, 'exercise_name': self.exercise_name,
                'equipment_id': self.equipment_id, 'date_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                'rfid': rfid, 'active': str(active)}
        response = requests.put(address, data=data)
        if response.status_code != 200 or response.status_code != 201:
            self.cache_request("put", address, data, str(response.status_code))
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
                'equipment_id': self.equipment_id, 'active': 'True'}
        response = requests.post(self.list_address, data=data)
        if response.status_code != 200 or response.status_code != 201:
            self.cache_request("post", self.list_address, data, str(response.status_code))
        return response

    def delete_set(self, set_id):
        """
        Sends a request to delete the set with the specified set_id.
        """
        address = self.detail_address + set_id
        response = requests.delete(address)
        print(response.content)
        if response.status_code != 200 or response.status_code != 201:
            self.cache_request("delete", address, "", str(response.status_code))
        return response

    def cache_request(self, method, address, data, status_code):
        """
        Caches a request if there is a connection error. Delete all prior cached messages that belong to the same
        set.
        """
        with open(self.cache_path, "w") as cache_file:
            cache_file.write(str(method) + "|" + str(address) + "|" + str(data) + "|" + status_code)
            cache_file.close()

    def empty_cache(self):
        """
        Tries to send all cached exercises to the server. Date values have to be updated then!
        :return:
        """
        pass
