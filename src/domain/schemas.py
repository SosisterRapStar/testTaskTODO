from pydantic import BaseModel, Field
from typing import List
import datetime
import uuid

class BaseUserModel(BaseModel):
    name: str


class Tag(BaseModel):
    name: str

class UserOnAuth(BaseUserModel):
    password: str

class UserOnResponse(BaseUserModel):
    pass

class NoteSchema(BaseModel):
    title: str
    tags: List[Tag]

class NoteSchemaOnResponse(NoteSchema):
    id: uuid.UUID

class NoteForUpdate(NoteSchema):
    title: str | None = None
    tags: List[Tag] | None = None


