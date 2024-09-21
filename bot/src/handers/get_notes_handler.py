from aiogram import Router, F, types
from src.simple_container import container
from aiogram.fsm.context import FSMContext
from src.keyboards.inline_keyboards import (
    NoteInlineBoard,
    CallBackDataDeleteMethod,
    CallBackDataUpdateMethod,
)
from src.keyboards.common_keyboards import get_auth_key_board
from src.schemas import NoteFromBackend, NoteToCreate
import copy
from .update_notes import start_updating_note
from typing import List
from src.backend_client import AuthorizationError
router = Router()


inline_board = NoteInlineBoard()


async def note_answer(message: types.Message, note: NoteToCreate):
    await message.answer(
            note_to_markdown(note=note),
            parse_mode="MarkdownV2",
            reply_markup=inline_board.get_note_inline_keyboard(note_id=note.id),
        )
    
def note_to_markdown(note: NoteToCreate) -> str:
    note = note.model_dump()
    note = {
        "title": "Sample Note",
        "tags": ["tag1", "tag2"],
        "content": "This is the content of the note.",
    }

    title = f"*{note['title']}*"
    tags = ", ".join([f"_{tag}_" for tag in note["tags"]])
    content = note["content"]

    markdown_text = f"{title}\n\n" f"Tags: {tags}\n\n" f"{content}"

    return markdown_text

# entrypoint
@router.message(F.text.lower() == "мои заметки")
async def get_users_notes(message: types.Message, state: FSMContext):
    try:
        list_notes = await container.notes_service.get_my_notes(
            user_id=message.from_user.id
        )
        for note in list_notes:
            await note_answer(message=message, note=note)
    except AuthorizationError:
        await message.answer("Вы не авторизованы", reply_markup=get_auth_key_board())
        
@router.message(F.text.lower() == "найти заметку по тегам")
async def get_users_notes_by_tags(message: types.Message, state: FSMContext):
    try:
        list_notes = await container.notes_service.get_my_notes(
            user_id=message.from_user.id
        )
        for note in list_notes:
            await note_answer(message=message, note=note)
    except AuthorizationError:
        await message.answer("Вы не авторизованы", reply_markup=get_auth_key_board())
        



@router.callback_query(CallBackDataUpdateMethod.filter())
async def update_note(
    callback_query: types.CallbackQuery,
    callback_data: CallBackDataUpdateMethod,
    state: FSMContext,
):
    note = await container.notes_service.get_note(
        user_id=callback_query.message.from_user.id, note_id=callback_data.note_id
    )
    note_in_dict = note.model_dump()
    await state.update_data(updating_note=note_in_dict)
    await callback_query.answer()
    await start_updating_note(message=callback_query.message, state=state)


@router.callback_query(CallBackDataDeleteMethod.filter())
async def delete_note(
    callback_query: types.CallbackQuery, callback_data: CallBackDataDeleteMethod
):
    await container.notes_service.delete_note(
        user_id=callback_query.message.from_user.id, note_id=callback_data.note_id
    )

    await callback_query.answer(text=f"Заметка удалена")

    await container.bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )


