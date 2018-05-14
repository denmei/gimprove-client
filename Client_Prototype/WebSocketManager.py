import asyncio
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory
import threading
import websocket
import logging


def on_close(ws):
    print("Websocket: closed")


class WebSocketManager(threading.Thread):
    """
    Builds a websocket connection to the server in a channel that's only visible for the current user. All detected
    repetitions and the weight will be communicated via this channel during a session."""

    def __init__(self, address, id):
        super(WebSocketManager, self).__init__()
        self.logger = logging.getLogger('gimprove' + __name__)
        self.address = address
        self.ws = websocket.WebSocketApp(self.address, on_close=on_close)
        self.logger.info("Websocket: Created connection to %s." % address)

    def run(self):
        self.ws.run_forever()

    def send(self, message):
        self.ws.send(str(message).encode())
        self.logger.info("Websocket: Sent message %s" % message)
