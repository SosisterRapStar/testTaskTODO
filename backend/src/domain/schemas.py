from pydantic import BaseModel, Field, ConfigDict
from typing import List
import datetime
import uuid


class BaseUserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class UserOnAuth(BaseUserModel):
    model_config = ConfigDict(from_attributes=True)
    password: str


class UserOnResponse(BaseUserModel):
    pass


class NoteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    tags: List[Tag]


class NoteSchemaOnResponse(NoteSchema):
    id: uuid.UUID


class NoteForUpdate(NoteSchema):
    title: str | None = None
    tags: List[Tag] | None = None
