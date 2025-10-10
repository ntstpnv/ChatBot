from sqlalchemy import CheckConstraint, Column, ForeignKey, SmallInteger, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {
        int: SmallInteger,
        str: String(40),
    }


ownerships = Table(
    "ownerships",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "word_id",
        ForeignKey("words.word_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    tele_id: Mapped[str] = mapped_column(String(20), unique=True)

    words: Mapped[list["Word"]] = relationship(
        secondary=ownerships,
        back_populates="users",
    )


class Word(Base):
    __tablename__ = "words"
    __table_args__ = (
        CheckConstraint("en_word ~ '^[a-z -]+$'"),
        CheckConstraint("ru_word ~ '^[а-яё -]+$'"),
    )

    word_id: Mapped[int] = mapped_column(primary_key=True)
    en_word: Mapped[str] = mapped_column(unique=True)
    ru_word: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list["User"]] = relationship(
        secondary=ownerships,
        back_populates="words",
    )
