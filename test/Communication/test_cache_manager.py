import unittest
from Client_Prototype.Communication.CacheManager import CacheManager
from Client_Prototype.Communication.RequestManager import RequestManager
from Client_Prototype.Communication.MessageQueue import MessageQueue
from Client_Prototype.Helpers.Configurator import Configurator
from pathlib import Path
import os
from shutil import copy2
import json
import requests
from mock import patch


class TestCacheManager(unittest.TestCase):

    def setUp(self):
        configurator = Configurator(config_path=str(Path(os.path.dirname(os.path.realpath(__file__))).parent)
                                                     + "/Configuration", config_file_name="config.json",
                                         api_links_name="api-links.json", environment="local")
        self.list_address, self.detail_address, self.userprofile_rfid_address, self.userprofile_detail_address, \
            self.websocket_address, self.token_address = configurator.get_api_links()
        self.exercise_name = 'Lat Pulldown'
        self.equipment_id = "653c9ed38b004f52bbc83fba95dc81cf"
        self.log_address = ""
        self.cache_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data"
        self.cache_file_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/client_cache.json"
        self.rfid = "0006921147"
        token = json.loads(requests.post(self.token_address, data={'username': "dennis", 'password': "blahblah"}).
                           content.decode()).get("token")
        self.header = {'Authorization': 'Token ' + str(token)}
        self.message_queue = MessageQueue()
        self.request_manager = RequestManager(exercise_name=self.exercise_name, equipment_id=self.equipment_id,
                                              cache_path=self.cache_path,
                                              message_queue=self.message_queue, configurator=configurator)
        self.cache_manager = CacheManager(self.cache_path, os.path.join(self.cache_path, "client_cache.json"), self.request_manager)
        copy2(str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/client_cache.json",
              str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/client_cache_cp.json")

        copy2(str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/fake_cache_test.json",
              str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/fake_cache_test_cp.json")

    @staticmethod
    def _get_cachefile_size_(path):
        """
        Counts lines of a text file.
        :return: 1 if number of lines <= 1, else number of lines.
        """
        with open(path) as count_file:
            return len(json.load(count_file))

    def test_cache_saving(self):
        size_prev = self._get_cachefile_size_(self.cache_file_path)
        self.cache_manager.update_cache_file()
        self.assertTrue(os.path.isfile(self.cache_file_path))
        self.assertEqual(size_prev, self._get_cachefile_size_(self.cache_file_path))

    def test_cache_set(self):
        """
        Tests whether test_cache_set-method writes cached requests into the specified file, only if there was a
        connection error.
        """
        count_begin = self._get_cachefile_size_(self.cache_file_path)
        self.cache_manager.cache_request(method="update", address=self.detail_address + "test",
                                           data={'weight': 10, 'rfid': '0006921147', 'active': 'False',
                                                 'exercise_name': 'Lat Pulldown', 'date_time': '2018-02-15T21:21:23Z',
                                                 'repetitions': 10, 'equipment_id': '1b7d032196154bd5a64c7fcfee388ec5'},
                                           status_code="500", set_id="test")
        count_after1 = self._get_cachefile_size_(self.cache_file_path)
        if count_after1 <= 1:
            self.assertEqual(count_begin, 1)
        else:
            self.assertTrue(count_after1 - 1 == count_begin)
        # successful requests may not be cached
        self.cache_manager.cache_request(method="update", address=self.detail_address + "test",
                                           data={'weight': 10, 'rfid': '0006921147', 'active': 'False',
                                                 'exercise_name': 'Lat Pulldown', 'date_time': '2018-02-15T21:21:23Z',
                                                 'repetitions': 10, 'equipment_id': '1b7d032196154bd5a64c7fcfee388ec5'},
                                           status_code="200", set_id="test")
        count_after2 = self._get_cachefile_size_(self.cache_file_path)
        self.assertEqual(count_after1, count_after2)

    def test_empty_cache(self):
        """
        Tests whether the test_empty_cache method reads all messages in the cache file and sends them, and removes them
        from the cache in the case of success.
        """
        self.cache_manager.empty_cache()

    @patch('Client_Prototype.Communication.RequestManager')
    def test_handle_fake_ids(self, mock_rm):
        """
        If a set could not be initialized properly, a fake id is used. Once there is a connection, the client manager
        must create a set with a valid id and with the latest data (repetitions, weight etc.) for this. In case of success,
        the corresponding messages have to be removed from the cache.
        """
        rm_mock = mock_rm()
        rm_mock.new_set.return_value = {'id': '8e7eb2e6-b269-44a5-a06a-3a5279975064',
                                        'date_time': '2018-06-10T10:17:59.615908+02:00',
                                        'durations': '[]',
                                        'exercise_unit': 'b7b9e045-0a25-4454-898d-0dfd2492384a',
                                        'repetitions': 0, 'weight': 0}
        rm_mock.update_set.return_value = {'status_code': 200}
        cache_manager = CacheManager(self.cache_path, os.path.join(self.cache_path, "fake_cache_test.json"), rm_mock)
        cache_manager.empty_cache()
        self.assertEqual(cache_manager.get_cache_size(), 1)
        rm_mock.new_set.assert_called_once_with(rfid='0006921147', exercise_unit="", cache=False)
        rm_mock.update_set.assert_called_once_with(active='True', cache=False,
                                                   durations=[0.564254, 0.422908, 0.426014, 0.450383, 0.48199, 0.42371, 0.446644, 0.426865, 0.416302],
                                                   end=True, repetitions=9, rfid='0006921147',
                                                   set_id='8e7eb2e6-b269-44a5-a06a-3a5279975064', weight=14.6)

    def test_handle_delete_messages(self):
        """

        :return:
        """
        pass

    def tearDown(self):
        os.remove(str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/client_cache.json")
        os.rename(str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/client_cache_cp.json",
                  str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/client_cache.json")

        os.remove(str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/fake_cache_test.json")
        os.rename(str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/fake_cache_test_cp.json",
                  str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/fake_cache_test.json")
