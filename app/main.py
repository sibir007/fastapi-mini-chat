from fastapi import FastAPI, Request, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.exceptions import TokenExpiredException, TokenNotFoundException
# from app.chat.router import router as chat_router
from simple_py_config import Config

config = Config()
config.from_dot_env_file('./.env')

app = FastAPI()
app.mount('/static', StaticFiles(directory='app/static'), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

from app.users.dependensies import get_current_user_id_dependence
from app.users.router import auth_api_router, users_api_router
app.include_router(auth_api_router)
app.include_router(users_api_router)
# app.include_router(chat_router)

from app.pages.router import router as page_router
app.include_router(page_router)


from app.chat.router import api_chat_router
app.include_router(api_chat_router)

# from app.websocket import ws_router
# app.include_router(ws_router)

# @app.get('/')
# async def redirect_to_auth():
#     return RedirectResponse(url='/auth')

# @app.exception_handler(TokenExpiredException)
# async def token_expired_exception_handler(
#     request: Request, 
#     exc: HTTPException
#     ):
#     return RedirectResponse(url='/auth')

# @app.exception_handler(TokenNotFoundException)
# async def token_not_found_exception_handler(
#     request: Request,
#     exc: HTTPException
#     ):
#     return RedirectResponse('/auth')




from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.responses import HTMLResponse

# app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:8000/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


# @app.get("/")
# async def get():
#     return HTMLResponse(html)


# async def get_cookie_or_token(
#     websocket: WebSocket,
#     session: Annotated[str | None, Cookie()] = None,
#     token: Annotated[str | None, Query()] = None,
# ):
#     if session is None and token is None:
#         raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
#     return session or token


# @app.websocket("/items/{item_id}/ws")
# async def websocket_endpoint(
#     *,
#     websocket: WebSocket,
#     item_id: str,
#     q: int | None = None,
#     cookie_or_token: Annotated[str, Depends(get_cookie_or_token)],
# ):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(
#             f"Session cookie or query token value is: {cookie_or_token}"
#         )
#         if q is not None:
#             await websocket.send_text(f"Query parameter q is: {q}")
#         await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")


class ConnectionManager:
    def __init__(self):
        
        self.active_connections: dict[int, list[WebSocket]]  = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        print(f'async def connect(self, user_id: int, websocket: WebSocket): pre')
        await websocket.accept()
        print(f'async def connect(self, user_id: int, websocket: WebSocket): past')
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if (connection_list:=self.active_connections.get(user_id)) is None:
            return
        connection_list.remove(websocket)
        if not connection_list:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
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


app.websocket('/ws/connect/{user_id}', name='WS')
async def websocket_endpoint(*,
    websocket: WebSocket, user_id: Annotated[int, Depends(get_current_user_id_dependence)]):
    print(f'async def websocket_endpoint(websocket: WebSocket, user_id: int): pre')
    await manager.connect(user_id, websocket)
    print(f'async def websocket_endpoint(websocket: WebSocket, user_id: int): past')
    try:
        while True:
            await websocket.receive()
            # websocket
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

    
