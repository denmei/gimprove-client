import requests
from datetime import datetime
import logging
import pytz
import json
from client_repo.Client_Prototype.Communication.WebSocketManager import WebSocketManager
from client_repo.Client_Prototype.Communication.CacheManager import CacheManager
import threading
import uuid
import os


class RequestManager(threading.Thread):
    """
    Caches messages that could not be sent to the server. Manages duplicates and the sequence of the messages.
    """
    def __init__(self, configurator, exercise_name, equipment_id, cache_path, message_queue):
        super(RequestManager, self).__init__()
        self.daemon = False
        self.logger = logging.getLogger('gimprove' + __name__)
        self.list_address, self.detail_address, self.userprofile_detail_address, self.userprofile_detail_address2, \
            self.websocket_address, token_address = configurator.get_api_links()
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id
        self.cache_manager = CacheManager(cache_path, os.path.join(cache_path, "client_cache.json"), self)
        self.message_queue = message_queue
        self.header = self.__init_header__(token_address, configurator.get_token(), configurator.get_username(),
                                           configurator.get_password())
        self.local_tz = pytz.timezone('Europe/Berlin')
        self.configurator = configurator
        self.websocket_manager = WebSocketManager(self.websocket_address, self.configurator.get_token())
        self.stop = False
        self.websocket_manager.setDaemon(True)
        self.websocket_manager.start()

    def run(self):
        self.cache_manager.empty_cache()
        while not self.stop:
            element = self.message_queue.get()
            if element is not None:
                self.__handle_message__(element)
        if self.stop:
            self.cache_manager.empty_cache()

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
            self.websocket_manager = WebSocketManager(self.websocket_address, self.configurator.get_token())
            self.websocket_manager.setDaemon(True)
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

    def update_set(self, repetitions, weight, set_id, rfid, active, durations, end, cache=True, websocket_send=True):
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
        print("UPDATE: %s" % set_id)
        address = self.detail_address + set_id
        data = {'repetitions': repetitions, 'weight': weight, "exercise": self.exercise_name,
                'equipment_id': self.equipment_id, 'date_time': str(self.local_tz.localize(datetime.now())),
                'rfid': rfid, 'active': str(active), 'durations': json.dumps(durations)}

        # send via websocket if requested
        if websocket_send:
            websocket_data = dict(list(data.items()) + list({'type': 'update', 'end': end, 'id': set_id}.items()))
            self.check_ws_connection()
            try:
                self.websocket_manager.send(json.dumps(websocket_data))
            except Exception as e:
                self.logger.debug("RequestManager: %s" % e)

        try:
            print(data)
            response = requests.put(address, data=data, headers=self.header)
            if response.status_code != 200 and response.status_code != 201 and cache:
                self.cache_manager.cache_request("update", address, data, str(response.status_code), set_id)
            self.logger.info("Sent update request. Data: %s, Status: %s, Reply: %s" % (str(data), response.status_code,
                                                                                       response.content))
            return response
        except requests.exceptions.RequestException as request_exception:
            self.logger.info("ConnectionError: %s" % request_exception)
            if cache:
                self.cache_manager.cache_request("update", address, data, '404', set_id)
            return None

    def new_set(self, rfid, exercise_unit="", cache=True, websocket_send=True):
        """
        Sends a request to create a new set.
        :param rfid: User-RFID
        :param exercise_unit: ID of exercise_unit the set belongs to (if not available: "")
        :return: New set id. Fake id in case of connection error.
        """
        data = {'exercise_unit': exercise_unit, 'repetitions': 0, 'weight': 0, 'exercise': self.exercise_name,
                'rfid': rfid, 'date_time': str(self.local_tz.localize(datetime.now())),
                'equipment_id': self.equipment_id, 'active': 'True', 'durations': json.dumps([])}

        # send via websocket if requested
        if websocket_send:
            websocket_data = dict(list(data.items()) + list({'type': 'new', 'end': str(False)}.items()))
            self.check_ws_connection()
            try:
                self.websocket_manager.send(json.dumps(websocket_data))
            except Exception as e:
                self.logger.debug("RequestManager: %s" % e)

        try:
            response = requests.post(self.list_address, data=data, headers=self.header)
            content = json.loads(response.content.decode("utf-8"))
            self.logger.info("Sent creation request. Status: %s" % response.status_code)
            if response.status_code == 401 and cache:
                new_uuid = str(uuid.uuid4()) + "_fake"
                self.cache_manager.cache_request("new", self.list_address, data, new_uuid, new_uuid)
                return {'id': new_uuid, 'date_time': datetime.now(), 'durations': '', 'exercise_unit': 'none',
                        'repetitions': 0, 'weight': 0}
            elif response.status_code != 200 and response.status_code != 201 and cache:
                self.cache_manager.cache_request("new", self.list_address, data, str(response.status_code), content['id'])
            return content
        except Exception as request_exception:
        # except requests.exceptions.RequestException as request_exception:
            new_uuid = str(uuid.uuid4()) + "_fake"
            self.logger.info("ConnectionError: %s" % request_exception)
            if cache:
                self.cache_manager.cache_request("new", self.list_address, data, new_uuid, new_uuid)
            return {'id': new_uuid, 'date_time': datetime.now(), 'durations': '', 'exercise_unit': 'none',
                    'repetitions': 0, 'weight': 0}

    def delete_set(self, set_id, cache=True):
        """
        Sends a request to delete the set with the specified set_id.
        """
        address = self.detail_address + set_id
        response = requests.delete(address, headers=self.header)
        # self.websocket_manager.send(set_id)
        try:
            if response.status_code != 200 and response.status_code != 201 and cache:
                self.cache_manager.cache_request("delete", address, "", str(response.status_code), set_id)
            return response
        except requests.exceptions.RequestException as request_exception:
            self.logger.info("ConnectionError: %s" % request_exception)
            if cache:
                self.cache_manager.cache_request("delete", address, "", "404", set_id)
            return None

    def quit(self):
        """
        :return:
        """
        self.stop = True
