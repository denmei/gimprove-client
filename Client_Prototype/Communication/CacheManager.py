import os
import logging
import json
from pandas.io.json import json_normalize, to_json
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
            self.cache += [{'no': 2, 'content': {'method': method, 'address': address, 'data': data,
                                                 'status_code': status_code, 'set_id': set_id}}]
            self.update_cache_file()
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

    def _handle_sets_with_fakeids_(self, cache_df):
        new_set_message_ids = list(cache_df[cache_df["content.method"] == 'new']['content.set_id'])
        relevant_data = cache_df[cache_df['content.set_id'].isin(new_set_message_ids)]
        new_set_messages = cache_df[cache_df["content.method"] == 'new']
        # get latest update message for each new set
        updates = relevant_data[relevant_data['content.method'] == 'update']
        latest_updates = updates[updates.groupby('content.set_id')['content.data.repetitions']
                                     .transform(max) == updates['content.data.repetitions']]
        # create sets and send the latest update message with the correct set_id. delete from cache if successful.
        delete_ids = []
        delete_rfids = []
        for i, row in new_set_messages.iterrows():
            rfid = row['content.data.rfid']
            set_id = row['content.set_id']
            if self.request_manager.rfid_is_valid(rfid):
                new_resp = self.request_manager.new_set(rfid=row['content.data.rfid'], exercise_unit="", cache=False)
                latest_update = latest_updates[latest_updates['content.set_id'] == row['content.set_id']]
                durations = list(map(float, latest_update['content.data.durations'].values[0].replace("[", "").replace("]", "").split(",")))
                update_resp = self.request_manager.update_set(repetitions=latest_update['content.data.repetitions'].values[0],
                                                              weight=latest_update['content.data.weight'].values[0],
                                                              set_id=new_resp['id'],
                                                              rfid=latest_update['content.data.rfid'].values[0],
                                                              active=latest_update['content.data.active'].values[0],
                                                              durations=durations,
                                                              end=True,
                                                              cache=False)
                if update_resp['status_code'] == 200 or update_resp['status_code'] == 201:
                    delete_ids += [set_id]
            else:
                delete_rfids += [rfid]
        cache_df_clean_ids = cache_df[~ cache_df['content.set_id'].isin(delete_ids)]
        cache_df_clean_rfids = cache_df_clean_ids[~ cache_df_clean_ids['content.data.rfid'].isin(delete_rfids)]
        return cache_df_clean_rfids

    def _handle_delete_sets_(self, cache_df):
        delete_set_message_ids = list(cache_df[cache_df["content.method"] == 'delete']['content.set_id'])
        relevant_data = cache_df[cache_df['content.set_id'].isin(delete_set_message_ids)]
        # delete all sets where a delete and a create message exist
        new_set_ids_to_delete = list(relevant_data[relevant_data['content.method'] == 'new']['content.set_id'])
        without_new_sets = relevant_data[~ relevant_data['content.set_id'].isin(new_set_ids_to_delete)]
        # delete all update messages where a delete message exists
        without_update_sets = without_new_sets[without_new_sets['content.method'] != 'update']
        # execute deletions and remove from cache if successful
        delete_set_ids = []
        for i, row in without_update_sets.iterrows():
            set_id = row['content.set_id']
            resp = self.request_manager.delete_set(set_id=set_id, cache=False)
            if resp['status_code'] in [200, 201]:
                delete_set_ids += [set_id]
        clean_cache = without_update_sets[~ without_update_sets['content.set_id'].isin(delete_set_ids)]
        return clean_cache

    def empty_cache(self):
        # TODO: For every new set, check whether there is already such a set before creating it
        # TODO: Always check whether the rfid is valid first. if not, remove all related requests!
        """
        Tries to send all cached exercises to the server. And deletes the messages.
        Attention: If requests fails, the request is written back to the cache -> not try again in the same session!
        :return: True if no error occured, else false.
        """
        cache_df = pd.DataFrame(json_normalize(self.cache))
        # TODO: send delete messages and remove all messages with the same set_id
        cache_df_deleted = self._handle_delete_sets_(cache_df)
        # add column for fake_id-state (true/false)
        cache_df_deleted['fake_id'] = cache_df_deleted['content.set_id'].apply(lambda x: "_fake" in x)
        cache_df_fakeids = self._handle_sets_with_fakeids_(cache_df_deleted)
        # TODO: send remaining update messages (only latest for each set)
        self.cache = cache_df_fakeids
        # self.update_cache_file()
        return True
