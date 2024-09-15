from passlib.context import CryptContext
from .exceptions import PasswordVerificationError



crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")






# хэшированный пароль должен поступать из базы данных
async def check_passwords(raw_password: str, hashed_password: str) -> None:
    if not crypt_context.verify(raw_password, hashed_password):
        raise PasswordVerificationError


async def hash_password(raw_password: str) -> str:
    return crypt_context.hash(raw_password)

