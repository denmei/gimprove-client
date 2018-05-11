import requests
from datetime import datetime
import os
import random
import traceback
import logging
import pytz
import json
from Client_Prototype.WebSocketManager import WebSocketManager


class RequestManager:
    """
    Caches messages that could not be sent to the server. Manages duplicates and the sequence of the messages.
    """

    def __init__(self, detail_address, list_address, websocket_address, userprofile_detail_address, exercise_name,
                 equipment_id, cache_path):
        self.logger = logging.getLogger('gimprove' + __name__)
        self.detail_address = detail_address
        self.list_address = list_address
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
        self.path = cache_path
        self.cache_path = os.path.join(cache_path, "client_cache.txt")
        self.userprofile_detail_address = userprofile_detail_address
        self._check_cache_file_()
        self.local_tz = pytz.timezone('Europe/Berlin')
        self.websocket_manager = WebSocketManager(websocket_address, equipment_id)

    def rfid_is_valid(self, rfid):
        """
        Checks whether there exists a Userprofile for a specific RFID.
        :return: True if there is an Userprofile with the RFID, else False.
        """
        response = requests.get(self.userprofile_detail_address + rfid)
        if response.status_code == 200:
            return True
        return False

    def _check_cache_file_(self):
        """
        Checks whether there is a cache_file in the specified directory. If not, a new file will be created.
        """
        if not os.path.isfile(self.cache_path):
            cache_file = open(self.cache_path, 'w')
            cache_file.close()

    def update_set(self, repetitions, weight, set_id, rfid, active, durations, end):
        """
        Update an existing set.
        :param repetitions: Repetitions count.
        :param weight: Weight used.
        :param set_id: ID of the set to update.
        :param rfid: RFID of the User.
        :param active: Specify whether set shall stay active or not.
        :param durations:
        :return: Server response.
        """
        address = self.detail_address + set_id
        data = {'repetitions': repetitions, 'weight': weight, "exercise_name": self.exercise_name,
                'equipment_id': self.equipment_id, 'date_time': str(self.local_tz.localize(datetime.now())),
                'rfid': rfid, 'active': str(active), 'durations': json.dumps(durations)}
        websocket_data = dict(list(data.items()) + list({'type': 'update', 'end': str(False)}.items()))
        self.websocket_manager.send(json.dumps(websocket_data))
        response = requests.put(address, data=data)
        if response.status_code != 200 and response.status_code != 201:
            self.cache_request("update", address, data, str(response.status_code))
        self.logger.info("Sent update request. Data: %s, Status: %s, Reply: %s" % (str(data), response.status_code, response.content))
        return response

    def new_set(self, rfid, exercise_unit=""):
        """
        Sends a request to create a new set.
        :param rfid: User-RFID
        :param exercise_unit: ID of exercise_unit the set belongs to (if not available: "")
        :return: Server response
        """
        data = {'exercise_unit': exercise_unit, 'repetitions': 0, 'weight': 0, 'exercise_name': self.exercise_name,
                'rfid': rfid, 'date_time': str(self.local_tz.localize(datetime.now())),
                'equipment_id': self.equipment_id, 'active': 'True', 'durations': json.dumps([])}
        websocket_data = dict(list(data.items()) + list({'type': 'new', 'end': str(False)}.items()))
        self.websocket_manager.send(json.dumps(websocket_data))
        response = requests.post(self.list_address, data=data)
        if response.status_code != 200 and response.status_code != 201:
            self.cache_request("new", self.list_address, data, str(response.status_code))
        self.logger.info("Sent creation request. Status: %s" % response.status_code)
        return response

    def delete_set(self, set_id):
        """
        Sends a request to delete the set with the specified set_id.
        """
        address = self.detail_address + set_id
        response = requests.delete(address)
        self.websocket_manager.send(set_id)
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
                cache_file.write(json.dumps({'method': method, 'address': address, 'data': data, 'status_code': status_code}) + "\n")
                cache_file.close()
            self.logger.info("Cached request.")
            return True
        else:
            return False

    def empty_cache(self):
        """
        Tries to send all cached exercises to the server. And deletes the messages.
        Attention: If requests fails, the request is written back to the cache -> not try again in the same session!
        :return: True if no error occured, else false.
        """
        os.rename(self.cache_path, self.path + "buffer_cache.txt")
        self._check_cache_file_()
        try:
            with open(self.path + "buffer_cache.txt", "r+") as cache_file:
                for line in cache_file:
                    message = json.loads(line)
                    response = None
                    method = message['method']
                    address = message['address']
                    data = message['data']
                    if message == 'update':
                        self.update_set(repetitions=data['repetitions'], weight=data['weight'],
                                        set_id=str(address.rsplit("/", 1))[1], rfid=data['rfid'], active=data['active'],
                                        durations=random.sample(range(1, 20), data['repetitions']), end=False)
                    elif method == 'new':
                        self.new_set(rfid=data['rfid'], exercise_unit=data['exercise_unit'])
                    elif method == 'delete':
                        self.delete_set(data['id'])
                    # if request was not successfull, try to cache it again
                    if response is not None:
                        status_code = response.status_code
                        self.cache_request(method, address, data, status_code)
                os.remove(self.path + "buffer_cache.txt")
                self.logger.info("Cache empty.")
                return True
        except Exception as e:
            print("Exception RequestManager: " + str(e))
            print(traceback.print_exc())
            # if an error occurs, recreate the cache and delete the buffer
            os.remove(self.cache_path)
            os.rename(self.path + "buffer_cache.txt", self.cache_path)
            self.logger.warning("Cache empty did not work.")
            return False
