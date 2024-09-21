from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_key_board():
    my_notes = KeyboardButton(text="Мои заметки")
    new_note = KeyboardButton(text="Новая заметка")

    row_notes = [my_notes, new_note]
    rows = [row_notes]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=rows)
    return markup


def get_auth_key_board():
    auth_button = KeyboardButton(text="Авторизоваться")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[auth_button]])
    return markup


def cancel_key():
    auth_button = KeyboardButton(text="Отмена")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[auth_button]])
    return markup
