from fastapi import APIRouter
from src.dependencies.db_services import notes_service, user_service
from src.dependencies.auth_deps import get_auth_user
from src.domain.schemas import NoteSchemaOnResponse, NoteSchema, NoteForUpdate
from starlette import status
from typing import List
from typing import Annotated
from fastapi import Query

router = APIRouter(tags=["Notes"])


@router.get(
    "/notes/", status_code=status.HTTP_200_OK, response_model=List[NoteSchemaOnResponse]
)
async def get_notes_by_tags(
    current_user: get_auth_user,
    note_service: notes_service,
    tags: Annotated[list[str] | None, Query(max_length=20)] = None,
):
    return await note_service.get_notes_by_tag(user_id=current_user.id, tags=tags)


@router.get("/notes/{note_id}", response_model=NoteSchemaOnResponse)
async def get_note(
    note_id: str, note_service: notes_service, current_user: get_auth_user
):
    return await note_service.get_user_note(current_user=current_user, id=note_id)


@router.post("/notes/", status_code=status.HTTP_201_CREATED)
async def create_note(
    current_user: get_auth_user, new_note: NoteSchema, note_service: notes_service
):
    await note_service.create_new_note(note=new_note, user=current_user)
    return {"message": "Note created"}


@router.put("/notes/{note_id}", status_code=status.HTTP_200_OK)
async def update_note(
    current_user: get_auth_user,
    note: NoteForUpdate,
    note_id: str,
    note_service: notes_service,
):
    await note_service.update_note()
    return {"message": "Note updated"}


@router.delete("/notes/{note_id}", status_code=status.HTTP_200_OK)
async def delete_note(
    note_id: str, note_service: notes_service, current_user: get_auth_user
):
    await note_service.delete_note(user=current_user, id=note_id)
    return {"message": "Note deleted"}


@router.get("/notes/me", response_model=List[NoteSchemaOnResponse])
async def get_all_users_notes(user_service: user_service, current_user: get_auth_user):
    return await user_service.get_users_notes(user=user_service)
