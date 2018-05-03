import asyncio
import websockets


class WebSocketManager:

    def __init__(self, address, port):
        self.server_socket = websockets.server.serve(self.handle_socket, address, port)
        asyncio.get_event_loop().run_until_complete(self.server_socket)

    async def handle_socket(self, socket, path):
        print("Init")
        received = await socket.recv()
        print(received)

    def send_update(self, repetitions):
        pass