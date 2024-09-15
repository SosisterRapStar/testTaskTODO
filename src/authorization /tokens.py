from datetime import timedelta, datetime
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.config import settings



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")