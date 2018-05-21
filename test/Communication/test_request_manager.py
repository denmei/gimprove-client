import unittest
from Client_Prototype.Communication.RequestManager import RequestManager
from Client_Prototype.Communication.MessageQueue import MessageQueue
import requests
import json
import random
import logging
from pathlib import Path
import os


class TestRequestManager(unittest.TestCase):
    # TODO: Check whether caching works when creating/updating/deleting

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
        self.detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"
        self.user_profile_rfid_address = "http://127.0.0.1:8000/tracker/userprofile_detail_rfid_rest/"
        self.user_profile_address = "http://127.0.0.1:8000/tracker/userprofile_detail_rest/"
        self.websocket_address = "ws://127.0.0.1:8000/ws/tracker/"
        self.exercise_name = 'Lat Pulldown'
        self.equipment_id = "653c9ed38b004f52bbc83fba95dc81cf"
        self.log_address = ""
        self.cache_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data"
        self.cache_file_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + \
                               "/test_data/client_cache.txt"
        self.rfid = "0006921147"
        self.message_queue = MessageQueue()
        self.request_manager = RequestManager(detail_address=self.detail_address, list_address=self.list_address,
                                              websocket_address=self.websocket_address,
                                              exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path=self.cache_path,
                                              userprofile_detail_address=self.user_profile_rfid_address,
                                              message_queue=self.message_queue)

    def tearDown(self):
        """
        Deletes chache file after tests.
        """
        pass
        # if os.path.isfile(self.cache_file_path):
        #   os.remove(self.cache_file_path)
        # TODO: Delete log-dummy


    def test_new_set(self):
        """
        Make request to create new set. Test whether set exists afterwards and did not before. New set must be
        user's active set after creation.
        """
        # get list of available sets
        sets_before = requests.get(self.list_address).content.decode("utf-8")
        # make request
        response = self.request_manager.new_set(rfid=self.rfid, exercise_unit="")
        content = json.loads(response.content.decode("utf-8"))
        set_id = content['id']
        # confirm that set_id is not in first list
        self.assertFalse(set_id in sets_before)
        # get list of available sets
        sets_after = requests.get(self.list_address).content.decode("utf-8")
        # confirm that set_id exists in second list
        self.assertTrue(set_id in sets_after)
        # confirm that new set is active set of user
        user_profile = requests.get(self.user_profile_rfid_address + self.rfid).content
        user_profile = json.loads(user_profile.decode("utf-8"))
        self.assertEqual(user_profile['_pr_active_set'], set_id)

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
        updated_set = requests.get(self.detail_address + content['id']).content
        updated_set = json.loads(updated_set.decode("utf-8"))
        user_profile = requests.get(self.user_profile_rfid_address + self.rfid).content
        user_profile = json.loads(user_profile.decode("utf-8"))
        self.assertEqual(updated_set['repetitions'], content['repetitions'] + 5)
        self.assertEqual(updated_set['weight'], content['weight'] + 5)
        self.assertEqual(user_profile['_pr_active_set'], None)

    def test_delete_set(self):
        """
        Tests whether sets are deleted properly.
        """
        # create a set
        response = self.request_manager.new_set(rfid=self.rfid, exercise_unit="")
        new_set = json.loads(response.content.decode("utf-8"))
        self.request_manager.delete_set(new_set['id'])
        # confirm that set is not in database anymore
        sets_after = requests.get(self.list_address).content.decode("utf-8")
        self.assertFalse(new_set['id'] in sets_after)

    def test_rfid_exists(self):
        """
        Tests whether requestmanager can distinguish real vs. non-real rfid-addresses.
        """
        # check whether return false for fake rfid
        fake_rfid = "0123456789"
        self.assertFalse(self.request_manager.rfid_is_valid(fake_rfid))

        # check whether returns true for correct rfid
        response = requests.get(self.user_profile_address + "1")
        real_rfid = json.loads(response.content.decode("utf-8"))['rfid_tag']
        self.assertTrue(self.request_manager.rfid_is_valid(real_rfid))
