from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.simple_container import container
from get_notes_handler import note_answer
from src.backend_client import AuthorizationError
from src.keyboards.common_keyboards import get_auth_key_board

router = Router()


# @router.message(F.text.lower() == "новая заметка")
# async def start_creating_note(message: Message, state: FSMContext):
#     try:
#         await container.auth_service.get_user_tokens(user_id=message.from_user.id)
#     except AuthorizationError:
#         await message.answer("Вы не авторизованы", reply_markup=get_auth_key_board())
#         return ...

#     await state.set_state(NoteCreator.title)
#     await message.answer("Введите заголовок", reply_markup=get_cancel_keyboard())
