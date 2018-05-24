import unittest
from Client_Prototype.Helpers.Configurator import Configurator
import json
from pathlib import Path
import os


class TestConfigurator(unittest.TestCase):

    def setUp(self):
        self.config_path = str(Path(os.path.dirname(os.path.realpath(__file__)))) + "/test_data"
        # save content of test-configuration
        with open(os.path.join(self.config_path, "config_test.json")) as config_file:
            self.data_saved = json.load(config_file)
            config_file.close()
        self.keys = self.__get_keys_from_file__(os.path.join(self.config_path, "config_test.json"))
        self.configurator = Configurator(config_path=self.config_path, config_file_name="config_test.json",
                                         api_links_name= "api-links_test.json", environment="local")

    def test_set_token(self):
        self.configurator.set_token("test-token")
        test_file = self.__read_json_testfile__()
        self.assertEqual(test_file['communication']['tokens']['local'], "test-token")
        self.assertTrue(self.__config_file_correct__(self.keys))

    def __config_file_correct__(self, keys):
        """
        Checks whether the config-file is correct.
        :param keys: Keys that must be in the config-file.
        :return: True if all keys are there, False otherwiese.
        """
        test_file = self.__read_json_testfile__()
        return keys == test_file.keys()

    def __read_json_testfile__(self):
        """
        Reads the current state of the json-File.
        :return: Json-Content as Dict.
        """
        with open(os.path.join(self.config_path, "config_test.json")) as config_file:
            test_file = json.load(config_file)
            config_file.close()
        return test_file

    def __get_keys_from_file__(self, json_path):
        """
        Returns the keys of the json-file.
        :param json_path: Path to the file.
        :return: List of the keys.
        """
        with open(json_path) as config_file:
            test_file = json.load(config_file)
            config_file.close()
        return test_file.keys()

    def tearDown(self):
        """
        Removes the test-copy.
        """
        try:
            os.remove(os.path.join(self.config_path, "config_test.json"))
        except:
            print("!!!!")
        with open(os.path.join(self.config_path, "config_test.json"), 'w') as config_file:
            json.dump(self.data_saved, config_file, indent=4)
            config_file.close()
