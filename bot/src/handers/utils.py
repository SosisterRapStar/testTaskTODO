from src.keyboards.inline_keyboards import NoteInlineBoard
from schemas import NoteToCreate
from aiogram import types


async def note_answer(message: types.Message, note: NoteToCreate):
    await message.answer(
        note_to_markdown(note=note),
        parse_mode="MarkdownV2",
        reply_markup=inline_board.get_note_inline_keyboard(note_id=note.id),
    )


inline_board = NoteInlineBoard()


def note_to_markdown(note: NoteToCreate) -> str:
    note = note.model_dump()
    note = {
        "title": "Sample Note",
        "tags": ["tag1", "tag2"],
        "content": "This is the content of the note.",
    }

    title = f"*{note['title']}*"
    tags = ", ".join([f"_{tag}_" for tag in note["tags"]])
    content = note["content"]

    markdown_text = f"{title}\n\n" f"Tags: {tags}\n\n" f"{content}"

    return markdown_text
