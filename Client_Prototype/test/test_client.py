import unittest
from Client_Prototype.Client import Equipment
import requests
from datetime import datetime
import json


class TestClient(unittest.TestCase):

    # TODO: Run-test with input-mockup

    def setUp(self):
        self.exercise_name = 'Lat Pulldown'
        self.equipment_id = "fded5e7ff5044992bb70949f3aec172c"
        self.equipment = Equipment(exercise_name=self.exercise_name, equipment_id=self.equipment_id)
        self.rfid = "0006921147"

        # self.list_address = "https://app-smartgym.herokuapp.com/tracker/set_list_rest/"
        self.list_address = "http://127.0.0.1:8000/tracker/set_list_rest/"
        # self.detail_address = "https://app-smartgym.herokuapp.com/tracker/set_detail_rest/"
        self.detail_address = "http://127.0.0.1:8000/tracker/set_detail_rest/"

    def test_init_set_record(self):
        """
        Check whether new set is created and a valid set_id ist returned when initializing a record. The new
        set must be activated. The weight and repetitions values must be equal to 0.
        """
        response_before = requests.get(self.list_address)
        set_data = self.equipment._init_set_record_(self.rfid)
        set_id = set_data['id']
        response_after = requests.get(self.list_address)
        self.assertTrue(set_id in str(response_after.content))
        self.assertTrue(set_id not in str(response_before.content))
        self.assertEqual(set_data['repetitions'], 0)
        self.assertEqual(set_data['weight'], 0)
        response_activity = requests.get("http://127.0.0.1:8000/tracker/userprofile_detail_rfid_rest/" + self.rfid)
        response_content = json.loads(response_activity.content.decode("utf-8"))
        self.assertEqual(str(set_id), response_content['active_set'])

    def test_delete_set(self):
        """
        Tests whether a created record can also be deleted.
        """
        # create set
        response_before = requests.get(self.list_address)
        data = self.equipment._init_set_record_(self.rfid)
        set_id = data['id']
        response_middle = requests.get(self.list_address)
        # deactivate set
        self.equipment._end_set_(rfid_tag=self.rfid, set_id=set_id, repetitions=10, weight=10)
        # delete set
        self.equipment._delete_set_(set_id)
        response_after = requests.get(self.list_address)
        self.assertEqual(len(response_after.content), len(response_before.content))
        self.assertTrue(len(response_middle.content) > len(response_before.content))
        self.assertTrue(len(response_middle.content) > len(response_after.content))