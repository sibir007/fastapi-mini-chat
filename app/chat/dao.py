from app.dao.base import BaseDAO
from app.chat.models import Message
from app.database import async_session_maker
from sqlalchemy import select, union_all

class MessageDAO(BaseDAO):
    model = Message

    @classmethod
    async def find_all_for_user_with_interlocutor(
            cls, user_id: int, interlocutor_id: int) -> list[Message]:
        async with async_session_maker() as session:
            query1 = select(cls.model)\
                .filter_by(sender_id=user_id, recipient_id=interlocutor_id)
            query2 = select(cls.model)\
                .filter_by(sender_id=interlocutor_id, recipient_id=user_id)
            u = union_all(query1, query2).order_by(Message.created_at)
            # u_sub = union_all(u).subquery()
            # query3 = select(u_sub)\
            #     .order_by(u_sub.c.created_at)
            stmt = select(Message).from_statement(u)
            result = await session.execute(stmt)
        return result.scalars()

    @classmethod
    async def find_all_for_user(cls, user_id: int) -> list[Message]:
        async with async_session_maker() as session:
            query1 = select(cls.model)\
                .filter_by(sender_id=user_id)
            query2 = select(cls.model)\
                .filter_by(recipient_id=user_id)
            u = union_all(query1, query2).order_by(Message.created_at)
            # u_sub = union_all(u).subquery()
            # query3 = select(u_sub)\
            #     .order_by(u_sub.c.created_at)
            stmt = select(Message).from_statement(u)
            result = await session.execute(stmt)
        return result.scalars()