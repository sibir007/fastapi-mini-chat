from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from app.exceptions import UserAlreadyExistException, IncorrectEmailOrPasswordException, PasswordMismatchException
# from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.chat.dao import MessageDAO
from app.users.dependensies import get_current_user_id_dependence
from app.chat.models import Message
from app.chat.schemas import MessageType, SInMessage, SOutMessage
from functools import reduce

api_chat_router = APIRouter(prefix='/api_v1/chat', tags=['Messages'])


@api_chat_router.post(
    '/send_message/',
    description='Отправка сообщения авторизованным пользователем')
async def send_message(
    out_message: SInMessage,
    sender_id: Annotated[int,
                         Depends(get_current_user_id_dependence)]) -> dict:
    await MessageDAO.add(sender_id=sender_id,
                         recipient_id=out_message.interlocutor_id,
                         content=out_message.content)
    # user: User = await UserDAO.find_one_or_none(email=user_data.email)

    # if user:
    #     raise UserAlreadyExistException

    # if user_data.password != user_data.password_check:
    #     raise PasswordMismatchException

    # hashed_password = get_password_hash(user_data.password)

    # await UserDAO.add(
    #     name=user_data.name,
    #     email=user_data.email,
    #     hashed_password=hashed_password
    # )

    return {'detail': 'Сообщение успешно отправлено'}


@api_chat_router.get(
    '/messages',
    response_model=list[SOutMessage],
    description=
    'Возвращает упорядоченную по времени создания переписку авторизованного пользователя, если указан ID - только переписку с пользователем с ID'
)
async def get_messages(
    user_id: Annotated[int, Depends(get_current_user_id_dependence)],
    interlocutor_id: Annotated[int | None, Query()] \
        = None) -> list[SOutMessage]:

    if interlocutor_id:
        raw_messages: list[Message] = \
            await MessageDAO.find_all_for_user_with_interlocutor(
                user_id=user_id,
                interlocutor_id=interlocutor_id
                )
    else:
        raw_messages: list[Message] = \
            await MessageDAO.find_all_for_user(user_id=user_id)

    messages: list[SOutMessage] = _convert_messages_format(
        user_id, raw_messages)
    # print(f'--------------messages: {messages}----------------')
    # messages.sort(key=lambda mess: mess.created)

    return messages


def _convert_messages_format(user_id: int,
                             raw_messages: list[Message]) -> list[SOutMessage]:
    # print(f'def _convert_messages_format raw_messages {raw_messages}')
    def reduce_function(accumulator: list[SOutMessage], raw_message: Message):
        # print(f'reduce_function(accumulator: list[SOutMessage], raw_message: Message): raw_message {raw_message}')

        if raw_message.sender_id == user_id:
            message = SOutMessage(type=MessageType.sent.value,
                                  created=raw_message.created_at,
                                  interlocutor_id=raw_message.recipient_id,
                                  content=raw_message.content)
        else:
            message = SOutMessage(type=MessageType.received.value,
                                  created=raw_message.created_at,
                                  interlocutor_id=raw_message.sender_id,
                                  content=raw_message.content)

        # message: SOutMessage = raw_message.sender_id == user_id \
        #     if SOutMessage(
        #         type=MessageType.sent.value,
        #         created=raw_message.created_at,
        #         interlocutor_id=raw_message.recipient_id,
        #         content=raw_message.content
        #         ) \
        #             else SOutMessage(
        #         type=MessageType.received.value,
        #         created=raw_message.created_at,
        #         interlocutor_id=raw_message.recipient_id,
        #         content=raw_message.content
        #         )
        accumulator.append(message)
        return accumulator

    converted_messages: list[SOutMessage] = reduce(reduce_function,
                                                   raw_messages, [])
    return converted_messages
