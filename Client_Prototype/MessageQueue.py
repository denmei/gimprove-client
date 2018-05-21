from queue import Queue


class MessageQueue:

    def __init__(self):
        self.message_queue = Queue()

    def put_update(self, repetitions, weight, set_id, rfid, active, durations, end):
        """
        Puts a new message on the queue.
        """
        message = {"type": "update", "repetitions": repetitions, "weight": weight, "set_id": set_id, "rfid": rfid,
                   "active": active, "durations": durations, "end": end}
        self.message_queue.put(message)

    def get(self):
        if not self.message_queue.empty():
            element = self.message_queue.get()
            self.message_queue.task_done()
            return element
        else:
            return None
