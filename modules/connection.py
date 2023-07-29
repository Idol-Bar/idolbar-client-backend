from fastapi import  WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict={}

    async def connect(self, websocket: WebSocket,client_id:str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, websocket: WebSocket,client_id:str):
        self.active_connections.pop(client_id)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send(self, message: str,client_id:str):
        connection = self.active_connections.get(client_id)
        for k in self.active_connections.keys():
            print(k)
            if k==client_id:
                print(f" client id ${client_id} equal ")
        if connection:
            await connection.send_text(message)
