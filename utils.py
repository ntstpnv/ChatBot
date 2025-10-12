from io import BytesIO
from random import choice
from re import fullmatch

from gtts import gTTS

from cache import VARIANTS


def check_en_word(en_word: str) -> bool:
    return bool(fullmatch(r"^[a-z -]+$", en_word))


def check_ru_word(ru_word: str) -> bool:
    return bool(fullmatch(r"^[а-яё -]+$", ru_word))


def unpack_words(words: list[tuple[str, str]]) -> tuple[str, list[str]]:
    return words[0][0], [word[1] for word in words]


def get_answers() -> dict[str, int]:
    return choice(VARIANTS)


def get_audio(en_word: str) -> BytesIO:
    buffer = BytesIO()
    gTTS(en_word).write_to_fp(buffer)
    buffer.seek(0)

    return buffer


def get_text(en_word: str, ru_words: list[str], answers: dict[str, int]) -> str:
    return (
        f"Выберите верный перевод\n"
        f"{en_word.upper()}\n\n"
        f"1 {ru_words[answers['1']].capitalize()}\n"
        f"2 {ru_words[answers['2']].capitalize()}\n"
        f"3 {ru_words[answers['3']].capitalize()}\n"
        f"4 {ru_words[answers['4']].capitalize()}"
    )
