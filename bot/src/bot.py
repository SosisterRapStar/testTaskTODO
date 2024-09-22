# from aiogram import Bot, Dispatcher, types
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import Message
# from aiogram.filters import Command
# import asyncio
# from src.config import settings


# bot = Bot(token=settings.api_key)
# dp = Dispatcher(storage=MemoryStorage())




# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())


from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
from src.keyboards.common_keyboards import get_main_key_board, get_auth_key_board
from src.handers.note_creat import router as note_creater_router
from src.handers.get_notes_handler import router as get_notes_router
from src.handers.update_notes import router as note_updator
from src.simple_container import container
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from src.backend_client import AuthorizationError, InvalidData
from aiogram.types import Message

dp = Dispatcher(storage=container.storage)

dp.include_router(note_creater_router)
dp.include_router(get_notes_router)
dp.include_router(note_updator)



@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Управляйте заметками", reply_markup=get_main_key_board())

class AuthorizationForm(StatesGroup):
    name = State()
    password = State()
    delete_password = State()

@dp.message(F.text.lower() == "авторизоваться")
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Введите логин")
    await state.set_state(AuthorizationForm.name)

@dp.message(AuthorizationForm.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите пароль")
    await state.set_state(AuthorizationForm.delete_password)

@dp.message(AuthorizationForm.delete_password)
async def delete_pass(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await container.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer("Сообщение с паролем было удален для безопасности")
    user_data = await state.get_data()
    try:
        tokens = await container.auth_service.authorize_user(user_id=message.from_user.id, password=user_data['password'], name=user_data['name'])
    except (AuthorizationError, InvalidData):
        await message.answer("Неправильный логин или пароль", reply_markup=get_auth_key_board())
        await state.clear()
        return ... 
    
    await message.answer(f"Вы авторизованы\n", reply_markup=get_main_key_board())
    await state.clear()


async def main():
    await dp.start_polling(container.bot)


if __name__ == "__main__":
    asyncio.run(main())
