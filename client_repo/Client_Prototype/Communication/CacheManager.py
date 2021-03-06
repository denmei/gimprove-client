import os
import logging
import json
from pandas.io.json import json_normalize, to_json
import pandas as pd
import threading
import traceback


class CacheManager:
    """
    Manages the cache that is used for http-requests that could not be sent successfully. 
    """

    def __init__(self, cache_path, cache_file_path, request_manager):
        self.lock = threading.Lock()
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
            with open(self.cache_path, 'w') as cache_file:
                cache_file.write("[]")
                cache_file.close()
            print("Create cache at: %s" % self.cache_path)
            return []
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
        set. Used locking to keep the method thread safe.
        """
        self.lock.acquire(True)
        try:
            if status_code[0] == "4" or ("_fake" in status_code):
                self.cache += [{'no': len(self.cache) +1, 'content': {'method': method, 'address': address, 'data': data,
                                                     'status_code': status_code, 'set_id': set_id}}]
                self.update_cache_file()
                self.lock.release()
                return True
            else:
                self.lock.release()
                return False
        except Exception as e:
            self.lock.release()
            return False

    def update_cache_file(self):
        with open(os.path.join(self.path, "delete.json"), 'w') as cache_file:
            if len(self.cache) > 0:
                # cache_file = self.cache.to_json()
                json.dump(self.cache, cache_file, indent=4)
            else:
                cache_file.write("[]")
            cache_file.close()
        try:
            os.remove(self.cache_path)
        except:
            pass
        os.rename(os.path.join(self.path, "delete.json"), self.cache_path)

    def _handle_sets_with_fakeids_(self, cache_df):
        """
        Empties cache for all sets with fake ids (new sets that could not be initialized on the server).
        For each new set, the new-set message and the latest update message are filtered and sent again. All other update
        messages are deleted from the cache. In case of success, also the two messages are deleted.
        All messages with an invalid rfid-tag are deleted.
        :param cache_df: Cache containing the cached messages. No delete-messages!
        :return: New cache with only relevant update messages.
        """
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
        try:
            for i, row in new_set_messages.iterrows():
                rfid = row['content.data.rfid']
                set_id = row['content.set_id']
                if self.request_manager.rfid_is_valid(rfid):
                    new_resp = self.request_manager.new_set(rfid=row['content.data.rfid'], exercise_unit="",
                                                            cache=False, websocket_send=False)
                    new_set_id = new_resp['id']
                    if '_fake' not in new_set_id:
                        latest_update = latest_updates[latest_updates['content.set_id'] == row['content.set_id']]
                        durations = list(map(float, latest_update['content.data.durations'].values[0].replace("[", "").replace("]", "").split(",")))
                        update_resp = self.request_manager.update_set(repetitions=latest_update['content.data.repetitions'].values[0],
                                                                      weight=latest_update['content.data.weight'].values[0],
                                                                      set_id=new_set_id,
                                                                      rfid=latest_update['content.data.rfid'].values[0],
                                                                      active=latest_update['content.data.active'].values[0],
                                                                      durations=durations,
                                                                      end=True,
                                                                      cache=False,
                                                                      websocket_send=False)
                        if update_resp is not None:
                            if update_resp.status_code in [200, 201]:
                                delete_ids += [set_id]
                else:
                    delete_rfids += [rfid]
            cache_df_clean_ids = cache_df[~ cache_df['content.set_id'].isin(delete_ids)]
            cache_df_clean_rfids = cache_df_clean_ids[~ cache_df_clean_ids['content.data.rfid'].isin(delete_rfids)]
            return cache_df_clean_rfids
        except Exception as e:
            self.logger.debug("Exception in _handle_sets_with_fakeids_: %s" % traceback.print_exc())
            cache_df_clean_ids = cache_df[~ cache_df['content.set_id'].isin(delete_ids)]
            cache_df_clean_rfids = cache_df_clean_ids[~ cache_df_clean_ids['content.data.rfid'].isin(delete_rfids)]
            return cache_df_clean_rfids

    def _handle_delete_sets_(self, cache_df):
        """
        Handles all messages where a set has to be deleted. First, all cached messages concerning the set are deleted.
        Then, the delete-message is sent. In case of success, also the delete message is removed from the cache.
        :param cache_df: Cache to be cleaned.
        :return: Cleaned cache.
        """
        delete_set_message_ids = list(cache_df[cache_df["content.method"] == 'delete']['content.set_id'])
        relevant_data = cache_df[cache_df['content.set_id'].isin(delete_set_message_ids)]
        # delete all sets where a delete and a create message exist
        new_set_ids_to_delete = set(relevant_data[relevant_data['content.method'] == 'new']['content.set_id'])
        without_new_sets = relevant_data[~ relevant_data['content.set_id'].isin(new_set_ids_to_delete)]
        # delete all update messages where a delete message exists
        without_update_sets = without_new_sets[without_new_sets['content.method'] != 'update']
        # execute deletions and remove from cache if successful
        delete_set_ids = []
        try:
            for i, row in without_update_sets.iterrows():
                set_id = row['content.set_id']
                resp = self.request_manager.delete_set(set_id=set_id, cache=False)
                if resp.status_code in [200, 201]:
                    delete_set_ids += [set_id]
            clean_cache = cache_df[(~ cache_df['content.set_id'].isin(delete_set_ids)) &
                                   (~ cache_df['content.set_id'].isin(new_set_ids_to_delete))]
            return clean_cache
        except Exception as e:
            self.logger.debug("Error in _handle_delete_sets_: %s" % traceback.print_exc())
            return cache_df[~ cache_df['content.set_id'].isin(new_set_ids_to_delete)]

    def _handle_update_sets_(self, cache_df):
        """
        Handles all update messages in the cache where there is no corresponding 'new'-message or 'delete'-message for
        the same set. First, the latest update message is filtered out for each set_id, all others are removed from the
        cache. The filtered messages get sent and in case of success removed from the cache.
        :param cache_df: Cache without any delete- or new messages.
        :return: cleaned cache.
        """
        # get latest update message for each set
        updates = cache_df[cache_df['content.method'] == 'update']
        others = cache_df[cache_df['content.method'] != 'update']

        # Filter for the latest update message of each set. First, take the one with the highest number of repetitions
        # (filtering for time might be critical due to http-latency). If there are multiple results, take the most
        # recent message.
        latest_updates_reps = updates[updates.groupby('content.set_id')['content.data.repetitions']
                                     .transform(max) == updates['content.data.repetitions']]
        latest_updates = latest_updates_reps[latest_updates_reps.groupby('content.set_id')['content.data.date_time']
                                     .transform(max) == latest_updates_reps['content.data.date_time']]
        delete_ids = []
        try:
            for i, row in latest_updates.iterrows():
                set_id = row['content.set_id']
                # TODO: Check whether set exists!
                durations = list(map(float, row['content.data.durations'].replace("[", "").replace("]", "").split(",")))
                update_resp = self.request_manager.update_set(
                    repetitions=row['content.data.repetitions'],
                    weight=row['content.data.weight'],
                    set_id=row['content.set_id'],
                    rfid=row['content.data.rfid'],
                    active=row['content.data.active'],
                    durations=durations,
                    end=True,
                    cache=False,
                    websocket_send=False)
                if update_resp is not None:
                    if update_resp.status_code in [200, 201]:
                        delete_ids += [set_id]
            cleaned_cache = latest_updates[~ latest_updates['content.set_id'].isin(delete_ids)].append(others)
            return cleaned_cache
        except Exception as e:
            self.logger.debug("Exception in _handle_update_sets_: %s" % traceback.print_exc())
            return latest_updates[~ latest_updates['content.set_id'].isin(delete_ids)].append(others)

    def empty_cache(self):
        # TODO: For every new set, check whether there is already such a set before creating it
        # TODO: Always check whether the rfid is valid first. if not, remove all related requests!
        """
        Tries to send all cached exercises to the server. And deletes the messages.
        Attention: If requests fails, the request is written back to the cache -> not try again in the same session!
        :return: True if no error occured, else false.
        """
        cache_df = pd.DataFrame(json_normalize(self.cache))
        self.logger.info("Cache: try empty cache.")
        if len(cache_df) > 0:
            # send delete messages and remove all messages with the same set_id
            cache_df_deleted = self._handle_delete_sets_(cache_df)
            # add column for fake_id-state (true/false)
            cache_df_deleted['fake_id'] = cache_df_deleted['content.set_id'].apply(lambda x: "_fake" in x)
            cache_df_fakeids = self._handle_sets_with_fakeids_(cache_df_deleted)
            # send remaining update messages (only latest for each set)
            cache_cleaned = self._handle_update_sets_(cache_df_fakeids)
            if len(cache_cleaned) < 1:
                self.cache = []
            else:
                self.cache = self.__df_to_dict__(cache_cleaned)
            self.update_cache_file()
        return True

    def __df_to_dict__(self, df):
        ret_dict = []
        k = 0
        for i, row in df.iterrows():
            new_entry = {}
            new_entry['content'] = {}
            new_entry['content']['address'] = row['content.address']
            new_entry['content']['data'] = {}
            new_entry['content']['data']['active'] = row['content.data.active']
            new_entry['content']['data']['date_time'] = row['content.data.date_time']
            new_entry['content']['data']['durations'] = row['content.data.durations']
            new_entry['content']['data']['equipment_id'] = row['content.data.equipment_id']
            new_entry['content']['data']['exercise_name'] = row['content.data.exercise_name']
            new_entry['content']['data']['repetitions'] = row['content.data.repetitions']
            new_entry['content']['data']['rfid'] = row['content.data.rfid']
            new_entry['content']['data']['weight'] = row['content.data.weight']
            new_entry['content']['method'] = row['content.method']
            new_entry['content']['set_id'] = row['content.set_id']
            new_entry['content']['status_code'] = row['content.status_code']
            new_entry['no'] = k
            ret_dict += [new_entry]
            k += 1
        return ret_dict
