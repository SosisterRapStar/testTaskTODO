from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.simple_container import container
import json

router = Router()


class NoteUpdator(StatesGroup):
    choice = State()
    change_title = State()
    change_tags = State()
    change_content = State()
    delete_tags = State()
    save = State()


def get_keyboard_for_update() -> types.ReplyKeyboardMarkup:
    content_update = KeyboardButton(text="Обновить содержимое")
    delete_tags = KeyboardButton(text="Удалить теги")
    update_tags = KeyboardButton(text="Добавить теги")
    rename = KeyboardButton(text="Переименовать заметку")
    cancel = KeyboardButton(text="Отменить")
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[content_update, delete_tags], [update_tags, rename], [cancel]],
    )
    return markup


def get_cancel_or_save_keyboard() -> types.ReplyKeyboardMarkup:
    cancel_button = KeyboardButton(text="Отменить")
    save_button = KeyboardButton(text="Сохранить")
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True, keyboard=[[cancel_button, save_button]]
    )
    return markup


def get_cancel_keyboard() -> types.ReplyKeyboardMarkup:
    cancel_button = KeyboardButton(text="Отменить")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[cancel_button]])
    return markup


def construct_keyboard(
    items: list[str], buttons_per_row: int = 3
) -> types.ReplyKeyboardMarkup:
    """
    Создает клавиатуру для удаления тегов
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for index, item in enumerate(items):
        row.append(types.KeyboardButton(text=item))
        if (index + 1) % buttons_per_row == 0 or (index + 1) == len(items):
            keyboard.add(*row)
            row = []
    keyboard.add([KeyboardButton(text="Отменить")])
    return keyboard


@router.message(Command("test_change"))
async def start_creating_note(message: Message, state: FSMContext):
    note_in_dict = {
        "content": "test",
        "tags": [
            "test",
        ],
        "title": "test_note",
    }
    await state.update_data(updating_note=note_in_dict)
    await state.set_state(NoteUpdator.choice)


@router.message(F.text.lower() == "обновить заметку")
async def start_creating_note(message: Message, state: FSMContext):
    await state.set_state(NoteUpdator.choice)


@router.message(NoteUpdator.choice, F.text.lower() == "отменить")
async def choice_state(message: Message, state: FSMContext):
    await cancel_process(message=message, state=state)


@router.message(NoteUpdator.choice, F.text.lower() == "обновить содержимое")
async def choice_state(message: Message, state: FSMContext):
    await state.set_state(NoteUpdator.change_content)
    await message.answer(
        "Напишите новое содержимое заметки", reply_markup=get_cancel_keyboard()
    )


@router.message(NoteUpdator.choice, F.text.lower() == "добавить тэг")
async def choice_state(message: Message, state: FSMContext):
    await state.set_state(NoteUpdator.change_tags)
    await message.answer("Введите новый тег", reply_markup=get_cancel_keyboard())


@router.message(NoteUpdator.choice, F.text.lower() == "удалить тэг")
async def choice_state(message: Message, state: FSMContext):
    data = await state.get_data()
    note = data["updating_note"]

    await state.set_state(NoteUpdator.delete_tags)
    await message.answer(
        "Выберите какой тэг удалить",
        reply_markup=construct_keyboard(items=note["tags"]),
    )


@router.message(NoteUpdator.choice, F.text.lower() == "переименовать заметку")
async def choice_state(message: Message, state: FSMContext):
    await state.set_state(NoteUpdator.change_title)
    await message.answer("Введите новое название", reply_markup=get_cancel_keyboard())


@router.message(NoteUpdator.change_content)
async def change_content(message: Message, state: FSMContext):
    data = await state.get_data()
    note = data["updating_note"]
    note["content"] = message
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.change_content, F.text.lower() == "отменить")
async def cancel_content(message: Message, state: FSMContext):
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.change_title)
async def change_title(message: Message, state: FSMContext):
    data = await state.get_data()
    note = data["updating_note"]
    note["title"] = message
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.change_title, F.text.lower() == "отменить")
async def cancel_title(message: Message, state: FSMContext):
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.change_tags)
async def add_tag(message: Message, state: FSMContext):
    data = await state.get_data()
    note = data["updating_note"]
    note["tags"].append(message)
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.change_tags, F.text.lower() == "отменить")
async def cancel_delete_tags(message: Message, state: FSMContext):
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.delete_tags)
async def delete_tag_action(message: Message, state: FSMContext):
    note = await state.get_data()
    if message.text not in note["tags"]:
        await state.set_state(NoteUpdator.choice)
        await message.answer("Такого тэга нет", reply_markup=get_keyboard_for_update())
    else:
        note["tags"].remove(message.text)
        await message.answer(
            "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
        )


@router.message(NoteUpdator.delete_tags, F.text.lower() == "отменить")
async def cancel_delete_tags(message: Message, state: FSMContext):
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.save)
async def save_note(message: Message, state: FSMContext):
    data = await state.get_data()
    note = data["updating_note"]
    await message.answer(json.dumps(), reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


async def cancel_process(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нечего отменять")
    else:
        await state.clear()
        await message.answer(
            "Процесс отменен", reply_markup=types.ReplyKeyboardRemove()
        )
