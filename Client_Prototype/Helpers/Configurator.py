import json
import os
import logging
from datetime import datetime
import requests


class Configurator:
    """
    Configuration class that handles all settings-related tasks and provides the necessary API-links.
    """

    def __init__(self, config_path, config_file_name, api_links_name, environment=None):
        self.config_path = config_path
        self.config_file_name = config_file_name
        self.api_links_name = api_links_name
        with open(os.path.join(config_path, config_file_name)) as config_file:
            self.configuration = json.load(config_file)
            config_file.close()
        with open(os.path.join(config_path, ".credentials.json")) as cred_file:
            self.credentials = json.load(cred_file)
            config_file.close()
        if environment is None:
            self.environment = str(self.configuration['communication']['environment']).lower()
        else:
            self.environment = environment
        self.links = self.__load_links__()
        self.__configure_logger__()

    def set_token(self, new_token):
        self.configuration['communication']['tokens'][self.environment] = new_token
        self.__update_file__()

    def get_password(self):
        return self.credentials['password']

    def get_username(self):
        return self.credentials['username']

    def get_token(self):
        token = self.configuration['communication']['tokens'][self.environment]
        if token == "":
            token = json.loads(requests.post(self.get_api_links()[5], data={'username': self.get_username(), 'password': self.get_password()})
                               .content.decode()).get("token")
            self.set_token(token)
        return token

    def get_environment(self):
        """
        Returns the current environment.
        :return: Current environment.
        """
        return self.environment

    def get_api_links(self):
        """
        Returns relevant API-links for the current environment
        :return: List of Api-Links: [Set_List, Set_Detail, Userprofile_Detail_RFID, Userprofile_Detail, Websocket, Token_Auth]
        """
        return self.links

    def __update_file__(self):
        """
        Updates the JSON-file for the configuration.
        """
        os.rename(os.path.join(self.config_path, self.config_file_name),
                  os.path.join(self.config_path, "del_config.json"))
        with open(os.path.join(self.config_path, self.config_file_name), 'w') as config_file:
            json.dump(self.configuration, config_file, indent=4)
            config_file.close()
        os.remove(os.path.join(self.config_path, "del_config.json"))

    def __load_links__(self):
        """
        Loads the links for the APIs of the GImprove-Server.
        :return [link set_list, link to set_detail, link to userprofile_detail(rfid)]
        """
        with open(os.path.join(self.config_path, self.api_links_name)) as links_file:
            if self.environment == 'test':
                links = json.load(links_file)['links']['test-links']
            elif self.environment == 'production':
                links = json.load(links_file)['links']['production-links']
            else:
                links = json.load(links_file)['links']['local-links']
        links_file.close()
        return links['set_list']['link'], links['set_detail']['link'], links['userprofile_detail']['link'], \
               links['userprofile_detail2']['link'], links['websocket']['link'], links['token_auth']['link']

    def __configure_logger__(self):
        """
        Configures and instantiates the logger.
        """
        # check whether log-directory exists:
        if "logs" not in os.listdir(self.config_path):
            os.mkdir(self.config_path + "/logs")

        # check whether logging file exists:
        log_name = "logging" + str(datetime.now().date()) + ".log"
        if log_name not in os.listdir(self.config_path + "/logs"):
            logging_file = open(self.config_path + "/logs/" + log_name, 'w')
            logging_file.close()

        logging.basicConfig(
            filename=self.config_path + "/logs/" + log_name,
            format="%(name)s %(levelname) - 10s %(asctime)s %(funcName)s %(message)s",
            level=logging.INFO
        )
