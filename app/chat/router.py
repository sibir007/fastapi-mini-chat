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
from app.websocket import manager as ws_manager

api_chat_router = APIRouter(prefix='/api_v1/chat', tags=['Messages'])


@api_chat_router.post(
    '/send_message/',
    description='Отправка сообщения авторизованным пользователем')
async def send_message(
    in_message: SInMessage,
    sender_id: Annotated[int,
                         Depends(get_current_user_id_dependence)]) -> dict:
    new_message: Message = await MessageDAO.add(
        sender_id=sender_id,
        recipient_id=in_message.interlocutor_id,
        content=in_message.content)
    
    new_message
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
    
    # # ws_message format
    # {
    #     'type': str ('new_message', 'new_user'),
    #     'message': { # for 'new_message' type
    #         type: str ('received' or 'sent')
    #         created: datetime
    #         interlocutor_id: int
    #         content: str
    #     }   
    # }

    sent_out_message = _create_sent_out_message(new_message)
    received_out_message = _create_received_out_message(new_message)
    ws_sent_message = _create_ws_out_message(sent_out_message)
    ws_received_message = _create_ws_out_message(received_out_message)
    await ws_manager.send_personal_message(sender_id, ws_sent_message)
    await ws_manager.send_personal_message(new_message.recipient_id, ws_received_message)
    
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
            message = _create_sent_out_message(raw_message)
        else:
            message = _create_received_out_message(raw_message)

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


# def convert_model_message_to_out(type: MessageType,
#                                   message: Message) -> SOutMessage:
#     out_message = SOutMessage(type=type,
#                               created=message.created_at,
#                               interlocutor_id=message.recipient_id,
#                               content=message.content)
#     return out_message


def _create_sent_out_message(model_message: Message):

    sent_out_message: SOutMessage = SOutMessage(
        type = MessageType.sent.value,
        created = model_message.created_at,
        interlocutor_id = model_message.recipient_id,
        content = model_message.content
    )
    
    return sent_out_message

def _create_received_out_message(model_message: Message):

    received_out_message: SOutMessage = SOutMessage(
        type = MessageType.received.value,
        created = model_message.created_at,
        interlocutor_id = model_message.sender_id,
        content = model_message.content
    )
    
    return received_out_message

def _create_ws_out_message(out_message: SOutMessage):

    return {
        'type': 'new_message',
        'message': out_message
    } 

# @ws_router.post('/send_message/',
#     description='Отправка сообщения авторизованным пользователем c последующей рассылкой клиентам через websocket. Для рассылки через websocket требуется предварительное установление websocket соединения "/ws/connect/{user_id}"'))
# async def wc_send_message(
#     # out_message: Annotated[SOutMessage, Depends(send_message)]):
#     in_message: SInMessage,
#     sender_id: Annotated[int,
#                          Depends(get_current_user_id_dependence)]) -> dict:
    
#     sender_message: SOutMessage = await send_message(in_message, sender_id)
    
#     receiver_id: int = sender_message.interlocutor_id
    
#     send_out_message: dict = {
#         'type': 'new_message',
#         'message': sender_message.model_dump() 
#     }
    
#     receiver_message: SOutMessage = sender_message.model_copy()
#     receiver_message.type = MessageType.received.value
#     receiver_message.interlocutor_id = sender_id
#     receiver_out_message: dict = {
#         'type': 'new_message',
#         'message': receiver_message.model_dump() 
#     }
    
#     manager.send_personal_message(sender_id, send_out_message)
#     manager.send_personal_message(receiver_id, receiver_out_message)
#     # sender_message.model_dump_json()
#     # # out message format
#     # {
#     #     type: str 'received' or 'sent'
#     #     created: datetime
#     #     interlocutor_id: int
#     #     content: str
#     # }
    


#     return sender_message
