from sqlalchemy import delete, func, Row, select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import CONFIG
from models import ownerships, User, Word

# async def create_tables():
#     async with CONFIG.ASYNC_ENGINE.begin() as connection:
#         await connection.run_sync(Base.metadata.drop_all)
#         await connection.run_sync(Base.metadata.create_all)


# async def insert_data():
#     async with AsyncSession(CONFIG.ASYNC_ENGINE) as session:
#         from qwert import a, b

# words = [Word(en_word=tpl[0], ru_word=tpl[1]) for tpl in zip(a, b)]
# user = User(tele_id="admin")

# user2 = User(tele_id="user123")
# user.words.extend(words)
# user2.words.extend(words)
# session.add_all([user, user2])

# user.words.extend(words)
# session.add(user)

# await session.commit()


async def init_user_if_not_exists(tele_id: str) -> None:
    async with AsyncSession(CONFIG.ASYNC_ENGINE) as async_session:
        check = await async_session.scalar(select(1).where(User.tele_id == tele_id))
        if check is None:
            admin = await async_session.scalar(
                select(User)
                .options(selectinload(User.words))
                .where(User.tele_id == "admin")
            )
            async_session.add(User(tele_id=tele_id, words=admin.words))
            await async_session.commit()


async def get_words(tele_id: str, previous: set[str]) -> Sequence[Row]:
    async with AsyncSession(CONFIG.ASYNC_ENGINE) as async_session:
        users_cte = select(User.user_id).where(User.tele_id == tele_id).cte("users_cte")

        words_cte = (
            select(Word.word_id, Word.en_word, Word.ru_word)
            .where(Word.en_word.notin_(previous))
            .cte("words_cte")
        )

        query = (
            select(words_cte.c.en_word, words_cte.c.ru_word)
            .select_from(words_cte)
            .join(ownerships, ownerships.c.word_id == words_cte.c.word_id)
            .join(users_cte, users_cte.c.user_id == ownerships.c.user_id)
        )

        return (await async_session.execute(query)).all()


async def delete_word(tele_id: str, en_word: str) -> None:
    async with AsyncSession(CONFIG.ASYNC_ENGINE) as async_session:
        user_id = await async_session.scalar(
            select(User.user_id).where(User.tele_id == tele_id)
        )
        word_id = await async_session.scalar(
            select(Word.word_id).where(Word.en_word == en_word)
        )

        await async_session.execute(
            ownerships.delete().where(
                ownerships.c.word_id == word_id, ownerships.c.user_id == user_id
            )
        )

        check = await async_session.scalar(
            select(func.count()).where(ownerships.c.word_id == word_id)
        )
        if not check:
            await async_session.execute(delete(Word).where(Word.word_id == word_id))


# async def main():
#     t = perf_counter()
#     res, l = await get_words("123", set())
#     print(perf_counter() - t, l)
#     print(res)


# run(main())
