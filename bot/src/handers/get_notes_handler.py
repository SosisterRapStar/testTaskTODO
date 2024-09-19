from aiogram import Router, F, types
from src.simple_container import container
from aiogram.fsm.context import FSMContext
from src.keyboards.inline_keyboards import NoteInlineBoard
from src.schemas import NoteFromBackend
from typing import List

# router = Router()

# @router.message(F.text == "Мои заметки")
# async def get_all_user_notes(message: types.Message, state: FSMContext):
#     if not await state.get_data()
#     list_notes = await container.notes_service.get_my_notes(user_id)


# async def handle_notes(message: types.Message, note_data: List[NoteFromBackend]):
