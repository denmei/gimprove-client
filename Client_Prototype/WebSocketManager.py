import asyncio
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory
import threading


class ClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print("OPEN")
        # self.sendMessage(u'{"message":"hallo"}'.encode('utf8'))

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))


class WebSocketManager(threading.Thread):
    """
    Builds a websocket connection to the server in a channel that's only visible for the current user. All detected
    repetitions and the weight will be communicated via this channel during a session.
    """

    def __init__(self, address, id):
        super(WebSocketManager, self).__init__()
        print(address)
        self.factory = WebSocketClientFactory(address)
        self.factory.protocol = ClientProtocol
        self.address = address

    def send(self, message):
        pass

    def run(self):
        reactor.connectTCP('127.0.0.1', 8000, self.factory)
        reactor.run(installSignalHandlers=False)
