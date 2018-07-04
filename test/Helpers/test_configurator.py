import unittest
from Client_Prototype.Helpers.Configurator import Configurator
import json
from pathlib import Path
import os


class TestConfigurator(unittest.TestCase):

    def setUp(self):
        self.config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent) + "/Configuration"
        # save content of test-configuration
        with open(os.path.join(self.config_path, "config.json")) as config_file:
            self.data_saved = json.load(config_file)
            config_file.close()
        self.keys = self.__get_keys_from_file__(os.path.join(self.config_path, "config.json"))
        self.configurator = Configurator(config_path=self.config_path, config_file_name="config.json",
                                         api_links_name="api-links.json", environment="local")

    def test_get_api_keys(self):
        """
        Tests whether all links from the api-links file are returned.
        """
        test_file = self.__read_json_testfile_api__()
        links_benchmark = test_file['links']['local-links']
        links = self.configurator.get_api_links()
        self.assertEqual(len(links), len(links_benchmark))

    def test_set_value_for_key(self):
        """
        Tests whether a value can be set properly in the configuration-file.
        """
        test_config = self.__read_json_testfile__()
        min_dist_val = test_config['sensor_settings']['distance_sensor']['min_dist']

        self.assertEqual(False, self.configurator.set_config_value("min_dist", "5"))
        test_config = self.__read_json_testfile__()
        self.assertEqual(test_config['sensor_settings']['distance_sensor']['min_dist'], min_dist_val)

        self.assertEqual(True, self.configurator.set_config_value("min_dist", 4))
        test_config = self.__read_json_testfile__()
        self.assertEqual(test_config['sensor_settings']['distance_sensor']['min_dist'], 4)

    def test_get_value_for_key(self):
        """
        Tests whether values can be returned properly from the config-file.
        """
        # Test for highest level of nested dict
        self.configurator.configuration['exercise_name'] = "test_name"
        self.assertEqual(self.configurator.get_value_for_key("exercise_name"), "test_name")

        # Test for lowest level of nested dict
        self.configurator.configuration['sensor_settings']['weight_sensor']['upper_border'] = 500
        self.assertEqual(self.configurator.get_value_for_key("upper_border"), 500)

        # Must return None if key not available
        self.assertEqual(self.configurator.get_value_for_key("not_there"), None)

    def __config_file_correct__(self, keys):
        """
        Checks whether the config-file is correct.
        :param keys: Keys that must be in the config-file.
        :return: True if all keys are there, False otherwiese.
        """
        # TODO: check rest of the kys
        test_file = self.__read_json_testfile__()
        return keys == test_file.keys()

    def __read_json_testfile__(self):
        """
        Reads the current state of the json-File.
        :return: Json-Content as Dict.
        """
        with open(os.path.join(self.config_path, "config.json")) as config_file:
            test_file = json.load(config_file)
            config_file.close()
        return test_file

    def __read_json__testcredentials__(self):
        """
        Reads the current state of the test-credentials.
        :return: Json-Content as Dict.
        """
        with open(os.path.join(self.config_path, ".credentials.json")) as credentials:
            test_file = json.load(credentials)
            credentials.close()
        return test_file

    def __read_json_testfile_api__(self):
        """
        Reads the current state of the json-File.
        :return: Json-Content as Dict.
        """
        with open(os.path.join(self.config_path, "api-links.json")) as config_file:
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
            os.remove(os.path.join(self.config_path, "config.json"))
        except Exception as e:
            print("Error when trying to delete config.json: " + str(e))
        with open(os.path.join(self.config_path, "config.json"), 'w') as config_file:
            json.dump(self.data_saved, config_file, indent=4)
            config_file.close()
