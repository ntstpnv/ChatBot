from asyncio import sleep

from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
)

from cache import REPLY_MARKUP
from config import TOKEN
from queries import add_word, delete_word, get_random_words, init_user_if_not_exists
from utils import (
    check_en_word,
    check_ru_word,
    get_answers,
    get_audio,
    get_text,
    unpack_words,
)


async def start(u: Update, c: CallbackContext) -> int:
    c.user_data["chat_id"] = u.message.chat_id

    c.user_data["tele_id"] = str(u.message.from_user.id)
    await init_user_if_not_exists(c.user_data["tele_id"])

    await sleep(0.2)
    c.user_data["message_id"] = (
        await u.message.reply_text("👋", reply_markup=REPLY_MARKUP.START)
    ).message_id

    return STATE1


async def preparation(u: Update, c: CallbackContext) -> int:
    await u.callback_query.answer()
    await u.callback_query.delete_message()
    answer = u.callback_query.data

    if answer == "1":
        words = await get_random_words(c.user_data["tele_id"], set())

        c.user_data["en_word"], ru_words = unpack_words(words)
        c.user_data["previous"] = {c.user_data["en_word"]}

        c.user_data["answers"] = get_answers()

        buffer = get_audio(c.user_data["en_word"])
        c.user_data["text"] = get_text(
            c.user_data["en_word"], ru_words, c.user_data["answers"]
        )

        await sleep(0.2)
        c.user_data["message_id"] = (
            await c.bot.send_voice(
                c.user_data["chat_id"],
                buffer,
                caption=c.user_data["text"],
                reply_markup=REPLY_MARKUP.QUESTION,
            )
        ).message_id

        return STATE4

    await sleep(0.4)
    c.user_data["message_id"] = (
        await c.bot.send_message(
            c.user_data["chat_id"],
            "Введите английское слово:",
        )
    ).message_id

    return STATE2


async def en_word(u: Update, c: CallbackContext) -> int:
    answer = u.message.text.lower()

    if check_en_word(answer):
        c.user_data["en_word"] = answer

        await sleep(0.4)
        await u.message.reply_text("Введите русский перевод:")

        return STATE3

    await sleep(0.4)
    await u.message.reply_text("Недопустимые символы! Введите английское слово:")

    return STATE2


async def ru_word(u: Update, c: CallbackContext) -> int:
    answer = u.message.text.lower()

    if check_ru_word(answer):
        await add_word(c.user_data["tele_id"], c.user_data["en_word"], answer)

        await sleep(0.2)
        await u.message.reply_text("Слово добавлено", reply_markup=REPLY_MARKUP.START)

        return STATE1

    await sleep(0.4)
    await u.message.reply_text("Недопустимые символы! Введите русский перевод:")

    return STATE3


async def next_word(u: Update, c: CallbackContext) -> int:
    await u.callback_query.answer()
    await u.callback_query.delete_message()
    answer = c.user_data["answers"].get(u.callback_query.data, -1)

    if answer > 0:
        buffer = get_audio(c.user_data["en_word"])
        text = f"{c.user_data['text']}\n\nОшибка! Попробуйте еще раз"

    elif not answer:
        words = await get_random_words(c.user_data["tele_id"], c.user_data["previous"])

        c.user_data["en_word"], ru_words = unpack_words(words)
        c.user_data["previous"].add(c.user_data["en_word"])

        c.user_data["answers"] = get_answers()

        buffer = get_audio(c.user_data["en_word"])
        text = c.user_data["text"] = get_text(
            c.user_data["en_word"], ru_words, c.user_data["answers"]
        )

    else:
        available = await delete_word(c.user_data["tele_id"], c.user_data["en_word"])

        words = await get_random_words(c.user_data["tele_id"], c.user_data["previous"])

        c.user_data["en_word"], ru_words = unpack_words(words)
        c.user_data["previous"].add(c.user_data["en_word"])

        c.user_data["answers"] = get_answers()

        buffer = get_audio(c.user_data["en_word"])
        c.user_data["text"] = get_text(
            c.user_data["en_word"], ru_words, c.user_data["answers"]
        )
        text = f"{c.user_data['text']}\n\nУдалено! Слов в словаре: {available}"

    await sleep(0.2)
    c.user_data["message_id"] = (
        await c.bot.send_voice(
            c.user_data["chat_id"],
            buffer,
            caption=text,
            reply_markup=REPLY_MARKUP.QUESTION,
        )
    ).message_id

    return STATE4


async def stop(update: Update, context: CallbackContext) -> int:
    await context.bot.delete_message(
        context.user_data["chat_id"], context.user_data["message_id"]
    )

    return ConversationHandler.END


if __name__ == "__main__":
    application = (
        Application.builder().rate_limiter(AIORateLimiter()).token(TOKEN).build()
    )

    conversation = ConversationHandler(
        [CommandHandler("start", start)],
        {
            (STATE1 := 1): [CallbackQueryHandler(preparation)],
            (STATE2 := 2): [MessageHandler(filters.TEXT & ~filters.COMMAND, en_word)],
            (STATE3 := 3): [MessageHandler(filters.TEXT & ~filters.COMMAND, ru_word)],
            (STATE4 := 4): [CallbackQueryHandler(next_word)],
        },
        [CommandHandler("stop", stop)],
    )

    application.add_handler(conversation)

    application.run_polling(drop_pending_updates=True)
