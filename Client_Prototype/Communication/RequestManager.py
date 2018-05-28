import requests
from datetime import datetime
import logging
import pytz
import json
from Client_Prototype.Communication.WebSocketManager import WebSocketManager
from Client_Prototype.Communication.CacheManager import CacheManager
import threading


class RequestManager(threading.Thread):
    """
    Caches messages that could not be sent to the server. Manages duplicates and the sequence of the messages.
    """
    def __init__(self, configurator, exercise_name, equipment_id, cache_path, message_queue):
        super(RequestManager, self).__init__()
        self.daemon = True
        self.logger = logging.getLogger('gimprove' + __name__)
        self.list_address, self.detail_address, self.userprofile_detail_address, self.userprofile_detail_address2, \
            self.websocket_address, token_address = configurator.get_api_links()
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
        self.cache_manager = CacheManager(cache_path, self)
        self.message_queue = message_queue
        self.header = self.__init_header__(token_address, configurator.get_token(), configurator.get_username(),
                                           configurator.get_password())
        self.local_tz = pytz.timezone('Europe/Berlin')
        self.websocket_manager = WebSocketManager(self.websocket_address, equipment_id)
        self.websocket_manager.setDaemon(True)
        self.websocket_manager.start()

    def run(self):
        while True:
            element = self.message_queue.get()
            if element is not None:
                self.__handle_message__(element)

    def __init_header__(self, token_address, token, user, password):
        """
        Creates the authentication header using the token. Gets a new token if passed token is None.
        :param token:
        :return:
        """
        return {'Authorization': 'Token ' + str(token)}

    def __handle_message__(self, message):
        """
        Handles a message from the message_queue.
        :param message:
        :return:
        """
        if "type" in message:
            type = message.get("type")
            if type == "update":
                self.update_set(message.get("repetitions"), message.get("weight"), message.get("set_id"),
                                message.get("rfid"), message.get("active"), message.get("durations"), message.get("end"))

    def check_ws_connection(self):
        if not self.websocket_manager.is_alive():
            self.websocket_manager.start()

    def rfid_is_valid(self, rfid):
        """
        Checks whether there exists a Userprofile for a specific RFID.
        :return: True if there is an Userprofile with the RFID, else False.
        """
        try:
            response = requests.get(self.userprofile_detail_address + rfid, headers=self.header)
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.RequestException as request_exception:
            # TODO: Appropriate exception handling
            self.logger.info("ConnectionError: %s" % request_exception)
            return True

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
        try:
            self.websocket_manager.send(json.dumps(websocket_data))
        except Exception as e:
            self.logger.debug("RequestManager: %s" % e)
        try:
            response = requests.put(address, data=data, headers=self.header)
            if response.status_code != 200 and response.status_code != 201:
                self.cache_manager.cache_request("update", address, data, str(response.status_code))
            self.logger.info("Sent update request. Data: %s, Status: %s, Reply: %s" % (str(data), response.status_code, response.content))
            return response
        except requests.exceptions.RequestException as request_exception:
            self.logger.info("ConnectionError: %s" % request_exception)
            self.cache_manager.cache_request("update", address, data, "x")
            return None

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
        try:
            self.websocket_manager.send(json.dumps(websocket_data))
        except Exception as e:
            self.logger.debug("RequestManager: %s" % e)
        try:
            response = requests.post(self.list_address, data=data, headers=self.header)
            if response.status_code != 200 and response.status_code != 201:
                self.cache_manager.cache_request("new", self.list_address, data, str(response.status_code))
            self.logger.info("Sent creation request. Status: %s" % response.status_code)
            return response
        except requests.exceptions.RequestException as request_exception:
            self.logger.info("ConnectionError: %s" % request_exception)
            self.cache_manager.cache_request("new", self.list_address, data, "x")
            return None

    def delete_set(self, set_id):
        """
        Sends a request to delete the set with the specified set_id.
        """
        address = self.detail_address + set_id
        response = requests.delete(address, headers=self.header)
        # self.websocket_manager.send(set_id)
        try:
            if response.status_code != 200 and response.status_code != 201:
                self.cache_manager.cache_request("delete", address, "", str(response.status_code))
            return response
        except requests.exceptions.RequestException as request_exception:
            self.logger.info("ConnectionError: %s" % request_exception)
            self.cache_manager.cache_request("delete", address, "", "x")
            return None
