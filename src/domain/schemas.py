from pydantic import BaseModel, Field
from typing import List
import datetime


class BaseUserModel(BaseModel):
    name: str

class Tag(BaseModel):
    name: str

class NoteSchema(BaseModel):
    title: str
    tags: List[Tag]


class UserInDB(BaseUserModel):
    id: str
    name: str
    password: str
    notes: List[NoteSchema] | None
    created_at: datetime.datetime
    updated_at: datetime.datetime