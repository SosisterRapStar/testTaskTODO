from aiogram import Router, F, types
from src.simple_container import container
from aiogram.fsm.context import FSMContext
from src.keyboards.inline_keyboards import (
    NoteInlineBoard,
    CallBackDataDeleteMethod,
    CallBackDataUpdateMethod,
)
from src.schemas import NoteFromBackend
import copy

from typing import List

router = Router()

# @router.message(F.text == "Мои заметки")
# async def get_all_user_notes(message: types.Message, state: FSMContext):
#     if not await state.get_data()
#     list_notes = await container.notes_service.get_my_notes(user_id)


# async def handle_notes(message: types.Message, note_data: List[NoteFromBackend]):
inline_board = NoteInlineBoard()


@router.message(F.text == "Мои заметки")
async def get_users_notes(message: types.Message, state: FSMContext):
    list_notes = await container.notes_service.get_my_notes(
        user_id=message.from_user.id
    )
    for note in list_notes:
        message.answer(
            f"{note.title}\n{','.join(note.tags)}\n{note.content}",
            reply_markup=inline_board.get_note_inline_keyboard(note_id=note.id),
        )


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
