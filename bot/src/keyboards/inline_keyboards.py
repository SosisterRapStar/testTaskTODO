from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters.callback_data import CallbackData

from dataclasses import dataclass


class CallBackDataDeleteMethod(CallbackData, prefix="delete_note"):
    note_id: str


class CallBackDataUpdateMethod(CallbackData, prefix="update_note"):
    note_id: str


@dataclass
class NoteInlineBoard:
    delete_text: str = "Удалить"
    update_text: str = "Изменить"
    update_callback: CallBackDataUpdateMethod = CallBackDataUpdateMethod
    delete_callback: CallBackDataDeleteMethod = CallBackDataDeleteMethod

    def get_note_inline_keyboard(self, note_id: str):
        delete_note_button = InlineKeyboardButton(
            text=self.delete_text,
            callback_data=self.delete_callback(note_id=note_id).pack(),
        )
        update_note_button = InlineKeyboardButton(
            text=self.update_text,
            callback_data=self.update_callback(note_id=note_id).pack(),
        )

        row_buttons = [delete_note_button, update_note_button]
        rows = [row_buttons]
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        return markup
