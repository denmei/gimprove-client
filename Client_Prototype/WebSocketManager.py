import asyncio
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory
import threading
import websocket
import logging
from websocket import create_connection

"""
class ClientProtocol(WebSocketClientProtocol):

    connections = list()

    def onOpen(self):
        print("OPEN")
        self.connections.append(self)
        print(self.connections)
        # self.sendMessage(u'{"message":"hallo"}'.encode('utf8'))

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
        # self.sendMessage(payload=payload)

    @classmethod
    def send(cls, message):
        payload = str(message).encode()
        for c in cls.connections:
            print("SENT")
            reactor.callFromThread(cls.sendMessage, c, payload)
"""


class WebSocketManager(threading.Thread):
    """
    Builds a websocket connection to the server in a channel that's only visible for the current user. All detected
    repetitions and the weight will be communicated via this channel during a session."""

    def __init__(self, address, id):
        super(WebSocketManager, self).__init__()
        self.logger = logging.getLogger('gimprove' + __name__)
        self.address = address
        self.ws = create_connection(self.address)
        self.logger.info("Websocket: Created connection.")

    def send(self, message):
        self.ws.send(str(message).encode())
        self.logger.info("Websocket: Sent message %s" % message)
