from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from datetime import datetime, time, timedelta, timezone
from simple_py_config import Config
from app.users.dao import UserDAO
from app.users.models import User


CONFIG: Config = Config.get_instance()
TOKEN_EXPIRE_DAYS = CONFIG.get('TOKEN_EXPIRE_DAYS')
SECRET_KEY = CONFIG.get('SECRET_KEY')
ALGORITHM = CONFIG.get('ALGORITHM')
PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')



def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
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