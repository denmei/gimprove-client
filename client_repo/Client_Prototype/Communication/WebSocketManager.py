import threading
import websocket
import logging


def on_close(ws):
    print("Websocket: closed")
    ws.close()


def on_error(ws):
    print("ERROR")
    ws.close()


class WebSocketManager(threading.Thread):
    """
    Builds a websocket connection to the server in a channel that's only visible for the current user. All detected
    repetitions and the weight will be communicated via this channel during a session."""

    def __init__(self, address, token):
        super(WebSocketManager, self).__init__()
        self.logger = logging.getLogger('gimprove' + __name__)
        self.address = address
        self.ws = websocket.WebSocketApp(self.address, on_close=on_close, on_error=on_error, header={'Authorization': 'Token ' + str(token)})
        self.logger.info("Websocket: Created connection to %s." % address)

    def run(self):
        self.ws.run_forever()

    def send(self, message):
        self.ws.send(str(message).encode())
        self.logger.info("Websocket: Sent message %s" % message)
