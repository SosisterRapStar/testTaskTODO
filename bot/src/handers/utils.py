from src.keyboards.inline_keyboards import NoteInlineBoard
from aiogram import types
from schemas import NoteToCreate

inline_board = NoteInlineBoard()

async def note_answer(message: types.Message, note: NoteToCreate):
    await message.answer(
        default_view(note=note),
        reply_markup=inline_board.get_note_inline_keyboard(note_id=note.id),
    )


def default_view(note: NoteToCreate):
    tags = ", ".join([f"{tag}" for tag in note.tags])
    string = f"{note.title}\n {tags}\n{note.content}."
    return string