# from asyncio import run
# from time import perf_counter

from sqlalchemy import delete, exists, func, select

# from admin_data import words
from config import ASYNC_ENGINE, ASYNC_SESSION
from models import Base, owners, User, Word


# async def create_tables():
#     async with ASYNC_ENGINE.begin() as connection:
#         await connection.run_sync(Base.metadata.drop_all)
#         await connection.run_sync(Base.metadata.create_all)


# async def init_admin():
#     async with ASYNC_SESSION.begin() as async_session:
#         async_session.add(
#             User(
#                 tele_id="admin",
#                 words=[Word(en_word=en, ru_word=ru) for en, ru in words],
#             )
#         )


# async def delete_user(tele_id: str) -> None:
#     async with ASYNC_SESSION.begin() as async_session:
#         statement = select(User).where(User.tele_id == tele_id)
#         user = await async_session.scalar(statement)
#         await async_session.delete(user)


async def init_user_if_not_exists(tele_id: str) -> None:
    async with ASYNC_SESSION.begin() as async_session:
        query = select(exists().where(User.tele_id == tele_id))
        user = await async_session.scalar(query)

        if not user:
            query = select(User).where(User.tele_id == "admin")
            admin = await async_session.scalar(query)

            user = User(tele_id=tele_id, words=admin.words)
            async_session.add(user)


async def get_random_words(tele_id: str, previous: set[str]) -> list[tuple[str, str]]:
    async with ASYNC_SESSION() as async_session:
        users_cte = select(User.user_id).where(User.tele_id == tele_id).cte()

        words_cte = (
            select(Word.word_id, Word.en_word, Word.ru_word)
            .where(Word.en_word.notin_(previous))
            .cte()
        )

        query = (
            select(words_cte.c.en_word, words_cte.c.ru_word)
            .join(owners, words_cte.c.word_id == owners.c.word_id)
            .join(users_cte, owners.c.user_id == users_cte.c.user_id)
            .order_by(func.random())
            .limit(4)
        )

        result = await async_session.execute(query)
        return result.all()


async def add_word(tele_id: str, en_word: str, ru_word: str) -> None:
    async with ASYNC_SESSION.begin() as async_session:
        query = select(User).where(User.tele_id == tele_id)
        user = await async_session.scalar(query)

        word_exists = any(word.en_word == en_word for word in user.words)
        if not word_exists:
            word = Word(en_word=en_word, ru_word=ru_word)
            user.words.append(word)


async def delete_word(tele_id: str, en_word: str) -> int:
    async with ASYNC_SESSION.begin() as async_session:
        query = select(User).where(User.tele_id == tele_id)
        user = await async_session.scalar(query)

        for word in user.words:
            if word.en_word == en_word:
                user.words.remove(word)
                break

        available = len(user.words)

        query = select(Word).where(Word.en_word == en_word)
        word = await async_session.scalar(query)

        if not word.users:
            query = delete(Word).where(Word.en_word == en_word)
            await async_session.execute(query)

        return available
