from passlib.context import CryptContext
from dataclasses import dataclass



@dataclass
class PasswordVerificationError(Exception):
    message: str
    def __str__(self) -> str:
        return super().__str__()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")






# хэшированный пароль должен поступать из базы данных
async def check_passwords(raw_password: str, hashed_password: str) -> bool:
    if not pwd_context.verify(raw_password, hashed_password):
        raise PasswordVerificationError