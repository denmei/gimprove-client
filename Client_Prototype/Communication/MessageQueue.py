from queue import Queue


class MessageQueue:

    def __init__(self):
        self.message_queue = Queue()

    def put_update(self, repetitions, weight, set_id, rfid, active, durations, end):
        """
        Puts a new update-message on the queue.
        :param repetitions: Number of repetitions.
        :param weight: Weight in kg.
        :param set_id: ID of the set to be updated.
        :param rfid: RFID of the user.
        :param active: True if still active, false otherwise.
        :param durations: Duration of each repetition. List of floats, length of list must be equal to number of
        repetitions.
        :param end: True if exercise shall be ended with this message.
        :return:
        """
        message = {"type": "update", "repetitions": repetitions, "weight": weight, "set_id": set_id, "rfid": rfid,
                   "active": active, "durations": durations, "end": end}
        self.message_queue.put(message)

    def get(self):
        """
        Returns an element from the queue.
        :return: Element from the queue if not empty, otherwise None.
        """
        if not self.message_queue.empty():
            element = self.message_queue.get()
            self.message_queue.task_done()
            return element
        else:
            return None
