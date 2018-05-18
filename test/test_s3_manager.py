import unittest
import logging
import os
from Client_Prototype.s3Manager import s3Manager
from pathlib import Path


class TestS3Manager(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.s3_manager = s3Manager("Test")

    def test_upload_to_s3(self):
        self.s3_manager.upload_logs_to_s3(os.path.join(str(Path(os.path.dirname(os.path.realpath(__file__)))),
                                                       "s3_test_files"))
