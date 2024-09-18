from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


async def get_note_inline_keyboard():
    delete_note_button = InlineKeyboardButton(text="Удалить")
    update_note_button = InlineKeyboardButton(text="Изменить")

    row_buttons = [delete_note_button, update_note_button]
    rows = [row_buttons]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
