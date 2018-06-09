import unittest
from Client_Prototype.Communication.RequestManager import RequestManager
from Client_Prototype.Communication.MessageQueue import MessageQueue
import requests
import json
import random
import logging
from pathlib import Path
import os
import time
import mock
from Client_Prototype.Helpers.Configurator import Configurator


def connection_error_update(address, data, headers):
    raise requests.exceptions.ConnectionError


def connection_error_new(address, data, headers):
    raise requests.exceptions.ConnectionError


class TestRequestManager(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.configurator = Configurator(config_path=str(Path(os.path.dirname(os.path.realpath(__file__))).parent)
                                                     + "/Configuration", config_file_name="config.json",
                                         api_links_name="api-links.json", environment="local")
        self.list_address, self.detail_address, self.userprofile_rfid_address, self.userprofile_detail_address, \
            self.websocket_address, self.token_address = self.configurator.get_api_links()
        self.exercise_name = 'Lat Pulldown'
        self.equipment_id = "653c9ed38b004f52bbc83fba95dc81cf"
        self.log_address = ""
        self.cache_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data"
        self.cache_file_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + \
                               "/test_data/client_cache.txt"
        self.rfid = "0006921147"
        self.message_queue = MessageQueue()
        self.request_manager = RequestManager(exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path=self.cache_path,
                                              message_queue=self.message_queue, configurator=self.configurator)
        token = json.loads(requests.post(self.token_address, data={'username': "dennis", 'password': "blahblah"}).
                           content.decode()).get("token")
        self.header = {'Authorization': 'Token ' + str(token)}

    def tearDown(self):
        """
        Deletes chache file after tests.
        """
        if os.path.isfile(self.cache_file_path):
            os.remove(self.cache_file_path)

    def get_cache_file(self):
        cache_list = []
        with open(self.cache_file_path, "r+") as cache_file:
            for line in cache_file:
                message = json.loads(line)
                cache_list.append(message)
            cache_file.close()
        return cache_list

    def test_new_set(self):
        """
        Make request to create new set. Test whether set exists afterwards and did not before. New set must be
        user's active set after creation.
        """
        # get list of available sets
        sets_before = requests.get(self.list_address, headers=self.header).content.decode("utf-8")
        # make request
        response = self.request_manager.new_set(rfid=self.rfid, exercise_unit="")
        content = json.loads(response.content.decode("utf-8"))
        set_id = content['id']
        # confirm that set_id is not in first list
        self.assertFalse(set_id in sets_before)
        # get list of available sets
        sets_after = requests.get(self.list_address, headers=self.header).content.decode("utf-8")
        # confirm that set_id exists in second list
        self.assertTrue(set_id in sets_after)
        # confirm that new set is active set of user
        user_profile = requests.get(self.userprofile_rfid_address + self.rfid, headers=self.header).content
        user_profile = json.loads(user_profile.decode("utf-8"))
        self.assertEqual(user_profile['_pr_active_set'], set_id)
        # TODO: Test Websocket-communication

    @mock.patch('requests.post', side_effect=connection_error_new)
    def test_new_set_wifilost(self, mock_get):
        """
        New Set-requests must be cached properly
        """
        cache_len_prev = len(self.get_cache_file())
        response = self.request_manager.new_set(rfid=self.rfid, exercise_unit="")
        cache = self.get_cache_file()
        last_cache_message = cache[len(cache) - 1]
        self.assertEqual(None, response)
        self.assertEqual("new", last_cache_message['method'])
        self.assertEqual(last_cache_message['data']['repetitions'], 0)
        self.assertEqual(last_cache_message['data']['rfid'], self.rfid)
        self.assertEqual(last_cache_message['data']['weight'], 0)
        self.assertEqual(cache_len_prev + 1, len(cache))

    def test_update_set(self):
        """
        All changes to a set must be applied and returned when executing a new server request.
        """
        response = self.request_manager.new_set(rfid=self.rfid, exercise_unit="")
        content = json.loads(response.content.decode("utf-8"))
        repetitions = content['repetitions'] + 5
        self.request_manager.update_set(repetitions=repetitions, weight=content['weight'] + 5,
                                        set_id=content['id'], rfid=self.rfid, active=False,
                                        durations=random.sample(range(1, 20), repetitions), end=False)
        updated_set = requests.get(self.detail_address + content['id'], headers=self.header).content
        updated_set = json.loads(updated_set.decode("utf-8"))
        user_profile = requests.get(self.userprofile_rfid_address + self.rfid, headers=self.header).content
        user_profile = json.loads(user_profile.decode("utf-8"))
        self.assertEqual(updated_set['repetitions'], content['repetitions'] + 5)
        self.assertEqual(updated_set['weight'], content['weight'] + 5)
        self.assertEqual(user_profile['_pr_active_set'], None)
        # TODO: Test Websocket-communication

    @mock.patch('requests.put', side_effect=connection_error_update)
    def test_update_set_wifilost(self, mock_put):
        """
        Update-request must be cached properly.
        """
        cache_len_prev = len(self.get_cache_file())
        response = self.request_manager.new_set(rfid=self.rfid, exercise_unit="")
        content = json.loads(response.content.decode("utf-8"))
        repetitions = content['repetitions'] + 5
        self.request_manager.update_set(repetitions=repetitions, weight=content['weight'] + 5,
                                        set_id=content['id'], rfid=self.rfid, active=False,
                                        durations=random.sample(range(1, 20), repetitions), end=False)
        cache = self.get_cache_file()
        last_cache_message = cache[len(cache) - 1]
        self.assertEqual(cache_len_prev + 1, len(cache))
        self.assertEqual(last_cache_message['data']['repetitions'], repetitions)
        self.assertEqual(last_cache_message['data']['rfid'], self.rfid)
        self.assertTrue(content['id'] in last_cache_message['address'])
        self.assertEqual(last_cache_message['method'], "update")
        self.assertEqual(last_cache_message['data']['weight'], content['weight'] + 5)

    def test_delete_set(self):
        """
        Tests whether sets are deleted properly.
        """
        # create a set
        response = self.request_manager.new_set(rfid=self.rfid, exercise_unit="")
        new_set = json.loads(response.content.decode("utf-8"))
        self.request_manager.delete_set(new_set['id'])
        # confirm that set is not in database anymore
        sets_after = requests.get(self.list_address, headers=self.header).content.decode("utf-8")
        self.assertFalse(new_set['id'] in sets_after)
        # TODO: Test Websocket-communication

    def test_delete_set_wifilost(self):
        # TODO: Delete-requests must be cached properly
        pass

    def test_rfid_exists(self):
        """
        Tests whether requestmanager can distinguish real vs. non-real rfid-addresses.
        """
        # check whether return false for fake rfid
        fake_rfid = "0123456789"
        self.assertFalse(self.request_manager.rfid_is_valid(fake_rfid))

        # check whether returns true for correct rfid
        response = requests.get(self.userprofile_detail_address, headers=self.header)
        real_rfid = json.loads(response.content.decode("utf-8"))['rfid_tag']
        self.assertTrue(self.request_manager.rfid_is_valid(real_rfid))

    def test_auth_error(self):
        """
        If requestmanager cannot authenticate and thus not send any message, all messages must be cached.
        """
        request_manager = RequestManager(exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                         cache_path=self.cache_path,
                                         message_queue=self.message_queue, configurator=self.configurator)
        cache_size_before = request_manager.cache_manager.get_cache_size()
        request_manager.new_set("test", "test")
        self.assertEqual(cache_size_before + 1, request_manager.cache_manager.get_cache_size())

    def test_thread_messaging(self):
        """
        Messages passed to the requestmanager's Messagequeue must be broadcasted to the server.
        """
        self.request_manager.start()
        response = self.request_manager.new_set(self.rfid)
        set_id = json.loads(response.content.decode("utf-8"))['id']
        repetitions_1 = json.loads(requests.get(self.detail_address + set_id, headers=self.header).content.decode()).get('repetitions')
        self.message_queue.put_update(repetitions=1, weight=10, set_id=set_id, rfid=self.rfid, active=False,
                                      durations=[0.1], end=False)
        time.sleep(1)
        repetitions_2 = json.loads(
            requests.get(self.detail_address + set_id, headers=self.header).content.decode()).get('repetitions')
        self.assertEqual(repetitions_1 + 1, repetitions_2)
