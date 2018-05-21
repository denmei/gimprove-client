import unittest
from Client_Prototype.Communication.CacheManager import CacheManager
from Client_Prototype.Communication.RequestManager import RequestManager
from Client_Prototype.Communication.MessageQueue import MessageQueue
from pathlib import Path
import os


class TestCacheManager(unittest.TestCase):

    def setUp(self):
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
        self.cache_manager = CacheManager(self.cache_path, self.request_manager)

    def _count_file_lines(self, path):
        """
        Counts lines of a text file.
        :return: 1 if number of lines <= 1, else number of lines.
        """
        i = 0
        with open(path) as count_file:
            for i, l in enumerate(count_file):
                pass
            return i + 1

    def test_cache_set(self):
        """
        Tests whether test_cache_set-method writes cached requests into the specified file, only if there was a
        connection error.
        """
        count_begin = self._count_file_lines(self.cache_file_path)
        self.cache_manager.cache_request(method="update", address=self.detail_address + "test",
                                           data={'weight': 10, 'rfid': '0006921147', 'active': 'False',
                                                 'exercise_name': 'Lat Pulldown', 'date_time': '2018-02-15T21:21:23Z',
                                                 'repetitions': 10, 'equipment_id': '1b7d032196154bd5a64c7fcfee388ec5'},
                                           status_code="500")
        count_after1 = self._count_file_lines(self.cache_file_path)
        if count_after1 <= 1:
            self.assertEqual(count_begin, 1)
        else:
            self.assertTrue(count_after1 - 1 == count_begin)
        # successful requests may not be cached
        self.cache_manager.cache_request(method="update", address=self.detail_address + "test",
                                           data={'weight': 10, 'rfid': '0006921147', 'active': 'False',
                                                 'exercise_name': 'Lat Pulldown', 'date_time': '2018-02-15T21:21:23Z',
                                                 'repetitions': 10, 'equipment_id': '1b7d032196154bd5a64c7fcfee388ec5'},
                                           status_code="200")
        count_after2 = self._count_file_lines(self.cache_file_path)
        self.assertEqual(count_after1, count_after2)

    # TODO
    def test_empty_cache(self):
        """
        Tests whether the test_empty_cache method reads all messages in the cache file and sends them, and removes them
        from the cache in the case of success.
        """
        self.cache_manager.empty_cache()

    def tearDown(self):
        os.remove(str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data/client_cache.txt")
