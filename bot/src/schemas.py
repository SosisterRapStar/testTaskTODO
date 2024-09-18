from pydantic import BaseModel, Field
from typing import List
import uuid


class Tag(BaseModel):
    name: str


class NoteToCreate(BaseModel):
    title: str
    tags: List[Tag]
    content: str


class NoteFromBackend(NoteToCreate):
    id: uuid.UUID


class NoteForUpdate(NoteToCreate):
    id: uuid.UUID
    title: str | None = None
    tags: List[Tag] | None = None
    content: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expire_in: int


class UserData(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)
