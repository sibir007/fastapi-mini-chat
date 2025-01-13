# from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

# from app.chat.dao import MessageDAO
# from app.chat.schemas import MessageType, SInMessage, SOutMessage
# from app.users.dependensies import get_current_user_id_dependence
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
        print(f'async def connect(self, user_id: int, websocket: WebSocket): pre')
        await websocket.accept();
        if self.active_connections.get(user_id) is None:
            self.active_connections[user_id] = []
        print(f'async def connect(self, user_id: int, websocket: WebSocket): past')
        self.active_connections[user_id].append(websocket);

    def disconnect(self, user_id: int, websocket: WebSocket):
        if (connection_list:=self.active_connections.get(user_id)) is None:
            return
        connection_list.remove(websocket);
        if not connection_list:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        print(f'async def send_personal_message(self, user_id: int, message: dict):')
        if (connection_list:=self.active_connections.get(user_id)) is None:
            return
        
        for connection in connection_list:
            await connection.send_json(message)
    
    async def broadcast(self, message: dict):
        for user_id, connection_list in self.active_connections.items():
            for connection in connection_list:
                await connection.send_json(message)


manager = ConnectionManager()

# ws_router = APIRouter(prefix='/ws', tags=['Websocket'])
