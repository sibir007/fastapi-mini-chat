from app.dao.base import BaseDAO
from app.chat.models import Message

class MessageDAO(BaseDAO):
    model = Message