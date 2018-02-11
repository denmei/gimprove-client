import time
from Client_Prototype.WeightManager import WeightManager



class RepetitionManager:

    def __init__(self, client, timeout_delta=5):
        self.client = client
        self.weight_manager = WeightManager
        self.timeout_delta = timeout_delta

    def start(self, set_id, rfid_tag):
        # TODO: weightmanager calibration
        rep = 0
        weight = 0
        while rep < 5:
            rep += 1
            time.sleep(1)
            self.client.add_repetition(rfid_tag=rfid_tag, set_id=set_id, repetitions=rep, weight=weight)
        self.client.end_set(rfid_tag=rfid_tag, set_id=set_id, repetitions=rep, weight=weight)
