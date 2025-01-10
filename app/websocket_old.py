from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.chat.dao import MessageDAO
from app.chat.schemas import MessageType, SInMessage, SOutMessage
from app.users.dependensies import get_current_user_id_dependence
from app.chat.router import send_message
from enum import Enum
from pydantic import BaseModel, Field

class WSOutMessageType(str, Enum):
    new_message = 'new_message'
    new_user = 'new_user'


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

ws_router = APIRouter('/ws')


ws_router.websocket('/connect/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive()
            # websocket
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

    

@ws_router.post('/send_message/',
    description='Отправка сообщения авторизованным пользователем c последующей рассылкой клиентам через websocket. Для рассылки через websocket требуется предварительное установление websocket соединения "/ws/connect/{user_id}"'))
async def wc_send_message(
    # out_message: Annotated[SOutMessage, Depends(send_message)]):
    in_message: SInMessage,
    sender_id: Annotated[int,
                         Depends(get_current_user_id_dependence)]) -> dict:
    
    sender_message: SOutMessage = await send_message(in_message, sender_id)
    
    receiver_id: int = sender_message.interlocutor_id
    
    send_out_message: dict = {
        'type': WSOutMessageType.new_message.value,
        'message': sender_message.model_dump() 
    }
    
    receiver_message: SOutMessage = sender_message.model_copy()
    receiver_message.type = MessageType.received.value
    receiver_message.interlocutor_id = sender_id
    receiver_out_message: dict = {
        'type': WSOutMessageType.new_message.value,
        'message': receiver_message.model_dump() 
    }
    
    manager.send_personal_message(sender_id, send_out_message)
    manager.send_personal_message(receiver_id, receiver_out_message)
    # sender_message.model_dump_json()
    # # out message format
    # {
    #     type: str 'received' or 'sent'
    #     created: datetime
    #     interlocutor_id: int
    #     content: str
    # }
    


    return sender_message
