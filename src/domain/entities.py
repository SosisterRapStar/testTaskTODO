from dataclasses import dataclass
from typing import List
import datetime


@dataclass
class Note:
    id: str
    title: str
    tags: List[str]
    created_at_timestamp: datetime.datetime
    updated_at_timestamp: datetime.datetime


@dataclass
class User:
    id: str
    name: str
    password: str
    email: str
    