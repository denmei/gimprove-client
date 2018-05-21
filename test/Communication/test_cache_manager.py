
def test_cache_set(self):
    """
    Tests whether test_cache_set-method writes cached requests into the specified file, only if there was a
    connection error.
    """
    count_begin = self._count_file_lines(self.cache_file_path)
    self.request_manager.cache_request(method="update", address=self.detail_address + "test",
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
    self.request_manager.cache_request(method="update", address=self.detail_address + "test",
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
        self.request_manager.empty_cache()