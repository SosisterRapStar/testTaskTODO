from pydantic import BaseModel, Field
from typing import List


class BaseUserModel(BaseModel):
    name: str


class Tag(BaseModel):
    name: str


class NoteSchema(BaseModel):
    title: str
    tags: List[Tag]
