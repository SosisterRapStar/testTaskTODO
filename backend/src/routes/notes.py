from fastapi import APIRouter
from src.dependencies.db_services import notes_service, user_service
from src.dependencies.auth_deps import get_auth_user
from src.domain.schemas import NoteSchemaOnResponse, NoteSchema, NoteForUpdate
from starlette import status
from typing import List
from typing import Annotated
from fastapi import Query
from src.dependencies.db_services import session_dep
import uuid
from typing import Optional

router = APIRouter(tags=["Notes"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NoteSchemaOnResponse)
async def create_note(
    current_user: get_auth_user, new_note: NoteSchema, note_service: notes_service
):
    return await note_service.create_new_note(note=new_note, user=current_user)


@router.patch("/{note_id}", status_code=status.HTTP_200_OK)
async def update_note(
    current_user: get_auth_user,
    note: NoteForUpdate,
    note_id: uuid.UUID,
    note_service: notes_service,
    response_model=NoteSchemaOnResponse
):
    
    return await note_service.update_note(id=note_id, user=current_user, note_schema=note)


@router.delete("/{note_id}", status_code=status.HTTP_200_OK)
async def delete_note(
    note_id: uuid.UUID, note_service: notes_service, current_user: get_auth_user
):
    return await note_service.delete_note(user=current_user, id=note_id)


@router.get("/", response_model=List[NoteSchemaOnResponse])
async def get_all_users_notes(
    note_service: notes_service,
    current_user: get_auth_user,
    tag: Annotated[List[str] | None, Query()] = None,
):
    if not tag:
        return await note_service.get_users_notes(user=current_user)
    return await note_service.get_notes_by_tag(user=current_user, tags=tag)


@router.get("/{note_id}", response_model=NoteSchemaOnResponse)
async def get_note(
    note_id: uuid.UUID, note_service: notes_service, current_user: get_auth_user
):
    return await note_service.get_users_note(current_user=current_user, id=note_id)


# response_model=List[NoteSchemaOnResponse]
# @router.get(
#     "/", status_code=status.HTTP_200_OK)
# async def get_notes_by_tags(
#     current_user: get_auth_user,
#     note_service: notes_service,
# ):
#     return tags
#
