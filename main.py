from asyncio import sleep

from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from cache import REPLY_MARKUP
from config import CONFIG
from queries import delete_word, get_words, init_user_if_not_exists
from utils import get_answers, get_audio, get_random_words, get_text


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
        words = await get_words(c.user_data["tele_id"], set())

        c.user_data["en_word"], ru_words = get_random_words(words)
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

        return STATE2

    else:
        # кнопка добавить
        return ConversationHandler.END


async def next_word(u: Update, c: CallbackContext) -> int:
    await u.callback_query.answer()
    await u.callback_query.delete_message()
    answer = c.user_data["answers"].get(u.callback_query.data, -1)

    if answer > 0:
        buffer = get_audio(c.user_data["en_word"])
        text = f"{c.user_data['text']}\n\nОшибка! Попробуйте еще раз"

    elif not answer:
        words = await get_words(c.user_data["tele_id"], c.user_data["previous"])

        c.user_data["en_word"], ru_words = get_random_words(words)
        c.user_data["previous"].add(c.user_data["en_word"])

        c.user_data["answers"] = get_answers()

        buffer = get_audio(c.user_data["en_word"])
        text = c.user_data["text"] = get_text(
            c.user_data["en_word"], ru_words, c.user_data["answers"]
        )

    else:
        await delete_word(c.user_data["tele_id"], c.user_data["en_word"])

        words = await get_words(c.user_data["tele_id"], c.user_data["previous"])
        available = len(words)

        c.user_data["en_word"], ru_words = get_random_words(words)
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

    return STATE2


async def stop(update: Update, context: CallbackContext) -> int:
    await context.bot.delete_message(
        context.user_data["chat_id"], context.user_data["message_id"]
    )

    return ConversationHandler.END


if __name__ == "__main__":
    application = (
        Application.builder().rate_limiter(AIORateLimiter()).token(CONFIG.TOKEN).build()
    )

    conversation = ConversationHandler(
        [CommandHandler("start", start)],
        {
            (STATE1 := 1): [CallbackQueryHandler(preparation)],
            (STATE2 := 2): [CallbackQueryHandler(next_word)],
        },
        [CommandHandler("stop", stop)],
    )

    application.add_handler(conversation)

    application.run_polling(drop_pending_updates=True)
