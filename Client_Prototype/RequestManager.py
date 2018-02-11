import requests
from datetime import datetime


class RequestManager:
    """
    Caches messages that could not be sent to the server. Manages duplicates and the sequence of the messages.
    """
    # TODO: Persist cache

    def __init__(self, detail_address, list_address, exercise_name, equipment_id):
        self.detail_address = detail_address
        self.list_address = list_address
        self.exercise_name = exercise_name
        self.equipment_id = equipment_id

    def rfid_is_valid(self, rfid):
        return True

    def update_set(self, repetitions, weight, set_id, rfid, active):
        """
        Update an existing set.
        :param repetitions: Repetitions count.
        :param weight: Weight used.
        :param set_id: ID of the set to update.
        :param rfid: RFID of the User.
        :param active: Specify whether set shall stay active or not.
        :return: Server response.
        """
        address = self.detail_address + set_id
        response = requests.put(address, data={'repetitions': repetitions, 'weight': weight,
                                               'exercise_name': self.exercise_name, 'equipment_id': self.equipment_id,
                                               'date_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), 'rfid': rfid,
                                               'active': str(active)})
        return response

    def new_set(self, rfid, exercise_unit=""):
        """
        Sends a request to create a new set.
        :param rfid: User-RFID
        :param exercise_unit: ID of exercise_unit the set belongs to (if not available: "")
        :return: Server response
        """
        data = {'exercise_unit': exercise_unit, 'repetitions': 0, 'weight': 0, 'exercise_name': self.exercise_name,
                'rfid': rfid, 'date_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                'equipment_id': self.equipment_id, 'active': 'True'}
        response = requests.post(self.list_address, data=data)
        return response

    def cache_exercise(self):
        """
        Caches an exercise if there is a connection error. Delete all prior cached messages that belong to the same
        set."
        :return:
        """
        pass

    def empty_cache(self):
        """
        Tries to send all cached exercises to the server. Date values have to be updated then!
        :return:
        """
        pass
