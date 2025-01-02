from typing import Annotated
from fastapi import Request, HTTPException, status, Depends
from jose import ExpiredSignatureError, jwt, JWTError
from datetime import  datetime, timezone
from app.exceptions import TokenNotFoundException, UserNoteFoundException, NoJwtException, NoUserIdException, TokenExpiredException
from app.users.dao import UserDAO
from simple_py_config import Config

from app.users.models import User

CONFIG: Config = Config.get_instance()
TOKEN_EXPIRE_DAYS = CONFIG.get('TOKEN_EXPIRE_DAYS')
SECRET_KEY = CONFIG.get('SECRET_KEY')
ALGORITHM = CONFIG.get('ALGORITHM')



def get_token(request: Request):
    token = request.cookies.get('user_access_token')
    if not token:
        raise TokenNotFoundException
    return token


async def get_current_user(token: Annotated[str, Depends(get_token)]) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
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

