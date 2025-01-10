# from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

# from app.chat.dao import MessageDAO
# from app.chat.schemas import MessageType, SInMessage, SOutMessage
from app.users.dependensies import get_current_user_id_dependence
# from app.chat.router import send_message
# from enum import Enum
# from pydantic import BaseModel, Field

# class WSOutMessageBase(BaseModel):
#     type: WSOutMessageType = Field(..., description='Тип сообщения')
    
# class NewMessage(BaseModel):
#     type = WSOutMessageType.new_message.value
#     message: SOutMessage = Field





class ConnectionManager:
    def __init__(self):
        
        self.active_connections: dict[int, list[WebSocket]]  = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        for connection in self.active_connections[user_id]:
            connection.send_json(message)
    async def broadcast(self, message: dict):
        for user_id, connection_list in self.active_connections.items():
            for connection in connection_list:
                await connection.send_json(message)


manager = ConnectionManager()

ws_router = APIRouter(prefix='/ws', tags=['Websocket'])


ws_router.websocket('/connect/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive()
            # websocket
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

    