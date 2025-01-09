from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import datetime


class MessageType(str, Enum):
    received = 'received'
    sent = 'sent'



class SInMessage(BaseModel):
    interlocutor_id: int = Field(..., description='ID получателя сообщения')
    content: str = Field(..., min_length=1, max_length=200, description='Текст сообщения, от 1 до 200 знаков')

class SOutMessage(BaseModel):
      type: MessageType = Field(..., description='Тип сообщения: "received" или "sent"')
      created: datetime = Field(..., description='Дата и время создания сообщения') 
      interlocutor_id: int = Field(..., description='ID собеседника')
      content: str = Field(..., min_length=1, max_length=200, description='Текст сообщения, от 1 до 200 знаков')
