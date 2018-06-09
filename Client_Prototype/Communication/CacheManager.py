import os
import logging
import json
import traceback
import random
from pandas.io.json import json_normalize
import pandas as pd


class CacheManager:

    def __init__(self, cache_path, cache_file_path, request_manager):
        self.logger = logging.getLogger('gimprove' + __name__)
        self.path = cache_path
        self.cache_path = cache_file_path
        self.request_manager = request_manager
        self.cache = self._init_cache_()

    def _init_cache_(self):
        """
        Checks whether there is a cache_file in the specified directory. If not, a new file will be created.
        """
        if not os.path.isfile(self.cache_path):
            cache_file = open(self.cache_path, 'w')
            cache_file.close()
            return dict()
        else:
            with open(self.cache_path) as cache_file:
                cache = json.load(cache_file)
                cache_file.close()
            return cache

    def get_cache_size(self):
        return len(self.cache)

    def cache_request(self, method, address, data, status_code, set_id):
        """
        Caches a request if there is a connection/server error. Delete all prior cached messages that belong to the same
        set.
        """
        if status_code[0] == "5" or status_code[0] == "4" or ("_fake" in status_code):
            self.cache[len(self.cache) + 1] = {'method': method, 'address': address, 'data': data,
                                               'status_code': status_code, 'set_id': set_id}
            self.logger.info("Cached request.")
            return True
        else:
            return False

    def update_cache_file(self):
        print(os.listdir(self.path))
        with open(os.path.join(self.path, "delete.json"), 'w') as cache_file:
            json.dump(self.cache, cache_file, indent=4)
            cache_file.close()
        os.remove(self.cache_path)
        os.rename(os.path.join(self.path, "delete.json"), self.cache_path)
        print("OK")

    def empty_cache(self):
        """
        Tries to send all cached exercises to the server. And deletes the messages.
        Attention: If requests fails, the request is written back to the cache -> not try again in the same session!
        :return: True if no error occured, else false.
        """
        return True
        try:
            print(json_normalize(self.cache))
            cache_df = pd.DataFrame()
            with open(self.path + "buffer_cache.txt", "r+") as cache_file:
                for line in cache_file:
                    message = json.loads(line)
                    cache_df = cache_df.append(json_normalize(message))
                    print(json_normalize(message))
                    response = None
                    method = message['method']
                    address = message['address']
                    data = message['data']
                    if message == 'update':
                        self.request_manager.update_set(repetitions=data['repetitions'], weight=data['weight'],
                                                        set_id=str(address.rsplit("/", 1))[1], rfid=data['rfid'],
                                                        active=data['active'],
                                                        durations=random.sample(range(1, 20), data['repetitions']),
                                                        end=False)
                    elif method == 'new':
                        self.request_manager.new_set(rfid=data['rfid'], exercise_unit=data['exercise_unit'])
                    elif method == 'delete':
                        self.request_manager.delete_set(data['id'])
                    # if request was not successfull, try to cache it again
                    if response is not None:
                        status_code = response.status_code
                        self.cache_request(method, address, data, status_code)
                os.remove(self.path + "buffer_cache.txt")
                self.logger.info("Cache empty.")
                print(cache_df)
                return True
        except Exception as e:
            print("Exception RequestManager: " + str(e))
            print(traceback.print_exc())
            # if an error occurs, recreate the cache and delete the buffer
            os.remove(self.cache_path)
            os.rename(self.path + "buffer_cache.txt", self.cache_path)
            self.logger.warning("Cache empty did not work.")
            return False
