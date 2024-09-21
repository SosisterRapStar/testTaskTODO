from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.simple_container import container
from .utils import note_answer
from src.backend_client import AuthorizationError
from src.keyboards.common_keyboards import get_auth_key_board

router = Router()


class NoteCreator(StatesGroup):
    title = State()
    tags = State()
    content = State()


def get_add_tag_keyboard():
    button = KeyboardButton(text="Добавить тег")
    button2 = KeyboardButton(text="Сохранить заметку")
    cancel_button = KeyboardButton(text="Отменить")
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True, keyboard=[[button, button2], [cancel_button]]
    )
    return markup


def get_cancel_keyboard():
    cancel_button = KeyboardButton(text="Отменить")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[cancel_button]])
    return markup


@router.message(F.text.lower() == "новая заметка")
async def start_creating_note(message: Message, state: FSMContext):
    try:
        await container.auth_service.get_user_tokens(user_id=message.from_user.id)
    except AuthorizationError:
        await message.answer("Вы не авторизованы", reply_markup=get_auth_key_board())
        return ...

    await state.set_state(NoteCreator.title)
    await message.answer("Введите заголовок", reply_markup=get_cancel_keyboard())


@router.message(NoteCreator.title, F.text.lower() == "отменить")
async def cancel_title(message: Message, state: FSMContext):
    await cancel_process(message, state)


@router.message(NoteCreator.title)
async def set_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NoteCreator.content)
    await message.answer(
        "Введите содержимое заметки", reply_markup=get_cancel_keyboard()
    )


@router.message(NoteCreator.content, F.text.lower() == "отменить")
async def cancel_content(message: Message, state: FSMContext):
    await cancel_process(message, state)


@router.message(NoteCreator.content)
async def set_content(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await state.set_state(NoteCreator.tags)
    await message.answer(
        "Добавьте теги к заметке, либо сохраните её",
        reply_markup=get_add_tag_keyboard(),
    )


@router.message(NoteCreator.tags, F.text.lower() == "отменить")
async def cancel_tags(message: Message, state: FSMContext):
    await cancel_process(message, state)


@router.message(NoteCreator.tags, F.text.lower() == "сохранить заметку")
async def save_note(message: Message, state: FSMContext):
    user_data = await state.get_data()
    tags = user_data.get("tags", [])

    await message.answer(
        f"Заметка сохранена!\n", reply_markup=types.ReplyKeyboardRemove()
    )
    note_data = user_data.copy()
    note = await container.notes_service.create_note(note_data)
    await note_answer(note=note, message=message)
    await state.clear()


@router.message(NoteCreator.tags, F.text.lower() == "добавить тег")
async def add_tag_action(message: Message, state: FSMContext):
    await message.answer("Введите новый тэг")
    await state.set_state(NoteCreator.tags)


@router.message(NoteCreator.tags)
async def save_tag(message: Message, state: FSMContext):
    current_data = await state.get_data()

    tags = current_data.get("tags", [])
    tags.append(message.text)
    await state.update_data(tags=tags)

    await message.answer(
        f"Тег '{message.text}' добавлен.", reply_markup=get_add_tag_keyboard()
    )


async def cancel_process(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нечего отменять")
    else:
        await state.clear()
        await message.answer(
            "Процесс отменен", reply_markup=types.ReplyKeyboardRemove()
        )
