from aiogram import Router, F, types
from src.simple_container import container
from aiogram.fsm.context import FSMContext
from src.keyboards.inline_keyboards import (
    CallBackDataDeleteMethod,
    CallBackDataUpdateMethod,
)
from src.keyboards.common_keyboards import get_auth_key_board, get_main_key_board
from .update_notes import start_updating_note
from typing import List
from src.backend_client import AuthorizationError
from .utils import note_answer
router = Router()




# entrypoint
@router.message(F.text.lower() == "мои заметки")
async def get_users_notes(message: types.Message, state: FSMContext):
    try:
        list_notes = await container.notes_service.get_my_notes(
            user_id=message.from_user.id
        )
        if not list_notes:
            await message.answer("У вас еще нет заметок", reply_markup=get_main_key_board())

            return
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
        user_id=callback_query.from_user.id, note_id=callback_data.note_id
    )
    note_in_dict = note.model_dump()
    await state.update_data(updating_note=note_in_dict)
    await callback_query.answer()
    await start_updating_note(message=callback_query.message, state=state)


@router.callback_query(CallBackDataDeleteMethod.filter())
async def delete_note(
    callback_query: types.CallbackQuery, callback_data: CallBackDataDeleteMethod
):
    print("user =", callback_query.message.from_user.id)
    await container.notes_service.delete_note(
        user_id=callback_query.from_user.id, note_id=callback_data.note_id
    )

    await callback_query.answer(text=f"Заметка удалена")

    await container.bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )
