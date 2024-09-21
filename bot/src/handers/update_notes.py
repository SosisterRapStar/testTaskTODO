from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.simple_container import container
from .utils import note_answer

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
    delete_tags = KeyboardButton(text="Удалить тэг")
    update_tags = KeyboardButton(text="Добавить тэг")
    rename = KeyboardButton(text="Переименовать заметку")
    save = KeyboardButton(text="Сохранить")
    cancel = KeyboardButton(text="Отменить")
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[content_update, delete_tags], [update_tags, rename], [cancel, save]],
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

    rows = []
    row = []
    for index, item in enumerate(items):
        row.append(types.KeyboardButton(text=item))
        if (index + 1) % buttons_per_row == 0 or (index + 1) == len(items):
            rows.append(row)
            row = []
    rows.append([KeyboardButton(text="Отменить")])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=rows)
    return markup


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
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


async def start_updating_note(message: Message, state: FSMContext):
    await state.set_state(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
    )


@router.message(NoteUpdator.choice, F.text.lower() == "сохранить")
async def choice_state(message: Message, state: FSMContext):
    await state.set_state(NoteUpdator.save)
    await save_note(message, state)


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
    if note["tags"]:
        await state.set_state(NoteUpdator.delete_tags)
        await message.answer(
            "Выберите какой тэг удалить",
            reply_markup=construct_keyboard(items=note["tags"]),
        )
    else:
        await state.set_state(NoteUpdator.choice)
        await message.answer(
            "У заметки нет тэгов", reply_markup=get_keyboard_for_update()
        )


@router.message(NoteUpdator.choice, F.text.lower() == "переименовать заметку")
async def choice_state(message: Message, state: FSMContext):
    await state.set_state(NoteUpdator.change_title)
    await message.answer("Введите новое название", reply_markup=get_cancel_keyboard())


@router.message(NoteUpdator.change_content)
async def change_content(message: Message, state: FSMContext):
    data = await state.get_data()
    note = data["updating_note"]
    note["content"] = message.text
    await state.update_data(updating_note=note)
    await state.set_state(NoteUpdator.choice)
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
    note["title"] = message.text
    await state.update_data(updating_note=note)
    await state.set_state(NoteUpdator.choice)
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
    note["tags"].append(message.text)
    await state.update_data(updating_note=note)
    await state.set_state(NoteUpdator.choice)
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
    data = await state.get_data()
    note = data["updating_note"]
    if message.text not in note["tags"]:
        await state.set_state(NoteUpdator.choice)
        await message.answer("Такого тэга нет", reply_markup=get_keyboard_for_update())
    else:
        note["tags"].remove(message.text)
        await state.update_data(updating_note=note)
        await state.set_state(NoteUpdator.choice)
        await message.answer(
            "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
        )


@router.message(NoteUpdator.delete_tags, F.text.lower() == "отменить")
async def cancel_delete_tags(message: Message, state: FSMContext):
    await state.set_data(NoteUpdator.choice)
    await message.answer(
        "Выберите что изменить в заметке", reply_markup=get_keyboard_for_update()
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


@router.message(NoteUpdator.save)
async def save_note(message: Message, state: FSMContext):
    data = await state.get_data()
    note = data["updating_note"]
    await container.notes_service.change_note(
        new_data=note, user_id=message.from_user.id
    )
    note = await container.notes_service.get_note(note_id=data["id"])
    await message.answer("Заметка обновлена", reply_markup=types.ReplyKeyboardRemove())
    await note_answer(note=note, message=message)
    await state.clear()


@router.message(NoteUpdator.choice)
async def choice_state(message: Message, state: FSMContext):
    await message.answer("Изменение заметки отменено")
    await cancel_process(message=message, state=state)
