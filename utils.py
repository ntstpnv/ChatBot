from io import BytesIO
from random import choice, sample

from gtts import gTTS
from sqlalchemy import Row, Sequence

from cache import CACHE


def get_random_words(words: Sequence[Row]) -> tuple[str, list[str]]:
    random_words = sample(words, 4)
    return random_words[0][0], [word[1] for word in random_words]


def get_answers() -> dict[str, int]:
    return choice(CACHE.VARIANTS)


def get_audio(en_word: str) -> BytesIO:
    buffer = BytesIO()
    gTTS(en_word).write_to_fp(buffer)
    buffer.seek(0)

    return buffer


def get_text(en_word: str, ru_words: list[str], answers: dict[str, int]) -> str:
    return (
        f""
        f"Выберите верный перевод\n"
        f"{en_word.upper()}\n\n"
        f"1 {ru_words[answers['1']].capitalize()}\n"
        f"2 {ru_words[answers['2']].capitalize()}\n"
        f"3 {ru_words[answers['3']].capitalize()}\n"
        f"4 {ru_words[answers['4']].capitalize()}"
    )
