import time
from Client_Prototype.WeightManager import WeightManager
from threading import Thread
import os


class SendThread(Thread):

    def __init__(self, client, repetition, rfid, set_id, weight_manager):
        self.client = client
        self.repetition = repetition
        self.rfid_tag = rfid
        self.set_id = set_id
        self.weight_manager = weight_manager
        Thread.__init__(self)

    def run(self):
        # get weight
        current_weight = self.weight_manager.get_weight_fake()
        # send update
        self.client.add_repetition(rfid_tag=self.rfid_tag, set_id=self.set_id, repetitions=self.repetition, weight=current_weight)


class RepetitionManager:

    def __init__(self, client, timeout_delta=5):
        self.client = client
        self.weight_manager = WeightManager()
        self.timeout_delta = timeout_delta

    def start(self, set_id, rfid_tag):
        # TODO: weightmanager calibration
        os.chdir("/home/dennis/PycharmProjects/SmartGym_Client_Prototype/")
        rep = 0
        weight = 0
        with open('numbers.txt') as numbers:
            content = numbers.readlines()
        for c in content:
            print(c)
            rep += 1
            thread = SendThread(client=self.client, repetition=rep, rfid=rfid_tag, set_id=set_id, weight_manager=self.weight_manager)
            thread.start()
            time.sleep(0.5)
        self.client.end_set(rfid_tag=rfid_tag, set_id=set_id, repetitions=rep, weight=weight)
