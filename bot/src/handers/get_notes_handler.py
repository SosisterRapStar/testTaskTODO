from aiogram import Router, F, types
from src.simple_container import container
from aiogram.fsm.context import FSMContext
from src.keyboards.inline_keyboards import (
    NoteInlineBoard,
    CallBackDataDeleteMethod,
    CallBackDataUpdateMethod,
)
from src.schemas import NoteFromBackend, NoteToCreate
import copy

from typing import List

router = Router()




inline_board = NoteInlineBoard()



@router.message(F.text.lower() == "мои заметки")
async def get_users_notes(message: types.Message, state: FSMContext):
    list_notes = await container.notes_service.get_my_notes(
        user_id=message.from_user.id
    )
    for note in list_notes:
        await message.answer(note_to_markdown(note=note), parse_mode="MarkdownV2",
                             reply_markup=inline_board.get_note_inline_keyboard(note_id=note.id))

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

@router.callback_query(CallBackDataDeleteMethod.filter())
async def delete_note(
    callback_query: types.CallbackQuery, callback_data: CallBackDataDeleteMethod
):
    await container.notes_service.delete_note(
        user_id=callback_query.message.from_user.id, note_id=callback_data.note_id
    )
    await callback_query.answer(text=f"Note was deleted")
    await container.bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )
    await callback_query.answer()

def note_to_markdown(note: NoteToCreate) -> str:
    note = note.model_dump()
    note = {
        "title": "Sample Note",
        "tags": ["tag1", "tag2"],
        "content": "This is the content of the note."
    }
    
    title = f"*{note['title']}*"  
    tags = ', '.join([f"_{tag}_" for tag in note['tags']])  
    content = note['content']
    
    markdown_text = (
        f"{title}\n\n"  
        f"Tags: {tags}\n\n"  
        f"{content}" 
    )
    
    return markdown_text
