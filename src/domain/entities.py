from typing import List
from .orm import Base, created_at_timestamp, updated_at_timestamp
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, String
import uuid


class User(Base):
    __tablename__ = "user"
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str | None] 
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]


class Note(Base):
    __tablename__ = "note"
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    tags: Mapped[List["Tag"] | None] = relationship(
        back_populates="notes", secondary="note_tag"
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    notes: Mapped[List["Note"] | None] = relationship(
        back_populates="tags", secondary="note_tag"
    )


class NoteTagSecondary(Base):
    __tablename__ = "note_tag"
    __table_args__ = (
        UniqueConstraint(
            "tag_id",
            "note_id",
            name="unique_pair_keys",
        ),
    )
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    note_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("note.id", ondelete="CASCADE")
    )

    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"))
