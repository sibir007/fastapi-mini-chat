# fastapi-mini-chat

Простой мини-чат на FastApi

## Создание и настройка проекта

```txt
<!-- requirements.txt -->

fastapi==0.115.6
SQLAlchemy==2.0.36
alembic==1.14.0
pydantic[email]==2.10.4
bcrypt==4.2.1
passlib==1.7.4
python-jose==3.3.0
websockets==14.1
aiosqlite==0.20.0
Jinja2==3.1.5
simple_py_config==0.0.1
```

`pip install -r requirements.txt`

```.env
SECRET_KEY=jlkjdasSSSSkiidmn
ALGORITHM=HS256
```

```sh
# структура проекта
.
├── app
│   ├── chat
│   │   ├── dao.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── dao
│   │   ├── base.py
│   │   └── __init__.py
│   ├── database.py
│   ├── exceptions.py
│   ├── __init__.py
│   ├── main.py
│   ├── static
│   │   ├── js
│   │   │   ├── auth.js
│   │   │   └── chat.js
│   │   └── styles
│   │       ├── auth.css
│   │       └── chat.css
│   ├── templates
│   │   ├── auth.html
│   │   └── chat.html
│   └── users
│       ├── auth.py
│       ├── dao.py
│       ├── dependensies.py
│       ├── __init__.py
│       ├── models.py
│       ├── router.py
│       └── schemas.py
├── config.py
├── .env
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Блок работы с базой данной

```py
# database.py

from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

database_url = 'sqlite+aiosqlite:///db.sqlite3'
engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
```

## Описываем модели таблиц

### Модель пользователей:

```py
# app/users/models.py

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
```

### Модель сообщений:

```py
# app/chat/models.py
from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
```

## Настройка Alembic и первая миграция

`alembic init -t async migration`

стало 

```py
# migration/env.py

import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.database import Base, database_url
from app.users.models import User
from app.chat.models import Message


config = context.config
config.set_main_option("sqlalchemy.url", database_url)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

    
target_metadata = Base.metadata
```

`alembic revision --autogenerate -m "Initial revision"`

`alembic upgrade head`

## пропишем универсальные методы для взаимодействия с базой данных

```py
# app/dao/base.py


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        Аргументы:
            data_id: Критерии фильтрации в виде идентификатора записи.

        Возвращает:
            Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Список экземпляров модели.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, **values):
        """
        Асинхронно создает новый экземпляр модели с указанными значениями.

        Аргументы:
            **values: Именованные параметры для создания нового экземпляра модели.

        Возвращает:
            Созданный экземпляр модели.
        """
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_instance
```

## JWT-токены и работа с пользователями

```py
# app/users/dao.py

from app.dao.base import BaseDAO
from app.users.models import User


class UsersDAO(BaseDAO):
    model = User
```

```py
#app/users/auth.py

from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from datetime import datetime, time, timedelta, timezone
from simple_py_config import Config
from app.users.dao import UserDAO
from app.users.models import User


config: Config = Config.get_instance()
PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')



def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=config.get('TOKEN_EXPIRE_DAYS'))
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, key=config.get('SECRET_KEY'), algorithm=config.get('ALGORITHM'))
    return encode_jwt


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)

async def authenticate_user(email: EmailStr, password: str) -> User | None:
    user: User = await UserDAO.find_one_or_none(email=email)
    if not user or verify_password(plain_password=password, hashed_password=user.hashed_password):
        return None
    return user
```

## Пользовательские исключения в FastApi

```py
from fastapi import status, HTTPException


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек")


class TokenNoFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не найден")


UserAlreadyExistsException = HTTPException(status_code=status.HTTP_409_CONFLICT,
                                           detail='Пользователь уже существует')

PasswordMismatchException = HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Пароли не совпадают!')

IncorrectEmailOrPasswordException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                  detail='Неверная почта или пароль')

NoJwtException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                               detail='Токен не валидный!')

NoUserIdException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                  detail='Не найден ID пользователя')

ForbiddenException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав!')
```

## Описание файла с зависимостями

```py
# app/users/dependencies.py

from typing import Annotated
from fastapi import Request, HTTPException, status, Depends
from jose import ExpiredSignatureError, jwt, JWTError
from datetime import  datetime, timezone
from app.exceptions import TokenNotFoundException, UserNoteFoundException, NoJwtException, NoUserIdException, TokenExpiredException
from app.users.dao import UserDAO
from simple_py_config import Config

from app.users.models import User

config: Config = Config.get_instance()


def get_token(request: Request):
    token = request.cookies.get('user_access_token')
    if not token:
        raise TokenNotFoundException
    return token


async def get_current_user(token: Annotated[str, Depends(get_token)]) -> User:
    try:
        payload = jwt.decode(
            token, 
            config.get('SECRET_KEY'), 
            config.get('ALGORITHM')
            )
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise NoJwtException
    
    user_id: str = payload.get('sub')
    if not user_id:
        raise NoUserIdException
    
    user = await UserDAO.find_one_or_none_by_id(int(user_id))
    if not user:
        raise UserNoteFoundException
    return user
```

## Код файла main.py

```py
# app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.exceptions import TokenExpiredException, TokenNotFoundException
from app.users.router import router as users_router
from app.chat.router import router as chat_router
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

app.include_router(users_router)
app.include_router(chat_router)

@app.get('/')
async def redirect_to_auth():
    return RedirectResponse(url='/auth')

@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(
    request: Request, 
    exc: HTTPException
    ):
    return RedirectResponse(url='/auth')

@app.exception_handler(TokenNotFoundException)
async def token_not_found_exception_handler(
    request: Request,
    exc: HTTPException
    ):
    return RedirectResponse('/auth')
```

## опишем схемы Pydantic для работы с запросами для регистрации и авторизации пользователей

```py
# app/users/schemas.py

from pydantic import BaseModel, EmailStr, Field

class SInUserRegister(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(..., min_length=5, max_length=50, description='Пароль от 5 до 50 знаков')
    password_check: str = Field(..., min_length=5, max_length=50, description='Пароль от 5 до 50 знаков')
    name: str = Field(..., min_length=3, max_length=50, description='Имя, от 3 до 50 знаков')

class SInUserAuth(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(..., min_length=5, max_length=50, description='Пароль от 5 до 50 знаков')
```

### Эндпоинты для работы с пользователями (регистрация и авторизация)

```py
# app/users/router

from fastapi import  APIRouter, Response
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from app.exceptions import UserAlreadyExistException, IncorrectEmailOrPasswordException, PasswordMismatchException
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UserDAO
from app.users.models import User
from app.users.schemas import SInUserAuth, SInUserRegister

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/register/')
async def register_user(user_data: SInUserRegister) -> dict:
    user: User = await UserDAO.find_one_or_none(email=user_data.email)

    if user:
        raise UserAlreadyExistException
    
    if user_data.password != user_data.password_check:
        raise PasswordMismatchException
    
    hashed_password = get_password_hash(user_data.password)
    
    await UserDAO.add(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    return {'message': 'Вы успешно зарегистрированы'}


@router.post('/login/')
async def auth_user(response: Response, user_data: SInUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({'sub': str(check.id)})
    response.set_cookie(key='user_access_token', value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Успешная авторизация'}


@router.post('/logout/')
async def logout_user(response: Response):
    response.delete_cookie(key='user_access_token')
    return {'message': 'Пользователь успешно вышел из системы'}
```