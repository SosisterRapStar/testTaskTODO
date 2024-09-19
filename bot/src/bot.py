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


# class AuthorizationForm(StatesGroup):
#     name = State()
#     password = State()
#     delete_password = State()

# @dp.message(Command("auth"))
# async def start_registration(message: Message, state: FSMContext):
#     await message.answer("Please enter your name:")
#     await state.set_state(AuthorizationForm.name)

# @dp.message(AuthorizationForm.name)
# async def set_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await message.answer("Now, please enter your password:")
#     await state.set_state(AuthorizationForm.delete_password)

# @dp.message(AuthorizationForm.delete_password)
# async def delete_pass(message: Message, state: FSMContext):
#     await state.update_data(password=message.text)
#     await message.answer("Your password will be deleted in order of secure")
#     await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     user_data = await state.get_data()
#     await message.answer(f"Registration complete!\n")
#     await state.clear()


# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())


from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
from src.config import settings
from src.keyboards.common_keyboards import get_main_key_board
from src.handers.note_creat import router as note_creater_router
from src.simple_container import container

dp = Dispatcher(storage=container.storage)

dp.include_router(note_creater_router)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Choose a button:", reply_markup=get_main_key_board())
    await container.stora


async def main():
    await dp.start_polling(container.bot)


if __name__ == "__main__":
    asyncio.run(main())
