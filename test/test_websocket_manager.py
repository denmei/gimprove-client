import unittest
from Client_Prototype.WebSocketManager import WebSocketManager
import websockets
import asyncio


class TestWebSocketManager(unittest.TestCase):

    def setUp(self):
        print("l")
        self.web_socket_manager = WebSocketManager('localhost', 8001)
        self.web_socket_client = websockets.client
        print("KL")

    async def client_test(self):
        async with self.web_socket_client.connect('ws://localhost:8001') as websocket:
            websocket.send("hallo")

    def test_websocket(self):
        asyncio.get_event_loop().run_until_complete(self.client_test())
