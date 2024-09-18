from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from src.services.notes_service import UseCases
from src.bot import bot

router = Router()


class NoteCreator(StatesGroup):
    title = State()
    content = State()

@router.message(Command("auth"))
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Please enter your name:")
    await state.set_state(AuthorizationForm.name)

@router.message(AuthorizationForm.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Now, please enter your password:")
    await state.set_state(AuthorizationForm.delete_password)

@router.message(AuthorizationForm.delete_password)
async def delete_pass(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer("Your password will be deleted in order of secure")
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    user_data = await state.get_data()  
    await message.answer(f"Registration complete!\n"
                         f"Name: {user_data['name']}\n"
                         f"Password: {user_data['password']}\n")
    await state.clear()


class AddTag(StatesGroup):
    add_teg = State()
