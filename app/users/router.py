from fastapi import  APIRouter, Response
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from app.exceptions import UserAlreadyExistException, IncorrectEmailOrPasswordException, PasswordMismatchException
from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UserDAO
from app.users.models import User
from app.users.schemas import SInUserAuth, SInUserRegister

router = APIRouter(prefix='/api_v1/auth', tags=['Auth'])




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