from collections import namedtuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


CACHE = namedtuple(
    "Cache",
    [
        "VARIANTS",
    ],
)(
    (
        {"1": 0, "2": 1, "3": 2, "4": 3},
        {"1": 0, "2": 1, "3": 3, "4": 2},
        {"1": 0, "2": 2, "3": 1, "4": 3},
        {"1": 0, "2": 2, "3": 3, "4": 1},
        {"1": 0, "2": 3, "3": 1, "4": 2},
        {"1": 0, "2": 3, "3": 2, "4": 1},
        {"1": 1, "2": 0, "3": 2, "4": 3},
        {"1": 1, "2": 0, "3": 3, "4": 2},
        {"1": 1, "2": 2, "3": 0, "4": 3},
        {"1": 1, "2": 2, "3": 3, "4": 0},
        {"1": 1, "2": 3, "3": 0, "4": 2},
        {"1": 1, "2": 3, "3": 2, "4": 0},
        {"1": 2, "2": 0, "3": 1, "4": 3},
        {"1": 2, "2": 0, "3": 3, "4": 1},
        {"1": 2, "2": 1, "3": 0, "4": 3},
        {"1": 2, "2": 1, "3": 3, "4": 0},
        {"1": 2, "2": 3, "3": 0, "4": 1},
        {"1": 2, "2": 3, "3": 1, "4": 0},
        {"1": 3, "2": 0, "3": 1, "4": 2},
        {"1": 3, "2": 0, "3": 2, "4": 1},
        {"1": 3, "2": 1, "3": 0, "4": 2},
        {"1": 3, "2": 1, "3": 2, "4": 0},
        {"1": 3, "2": 2, "3": 0, "4": 1},
        {"1": 3, "2": 2, "3": 1, "4": 0},
    ),
)


REPLY_MARKUP = namedtuple(
    "ReplyMarkup",
    [
        "START",
        "QUESTION",
    ],
)(
    InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Открыть словарь", callback_data="1")],
            [InlineKeyboardButton("Добавить слово", callback_data="2")],
        ]
    ),
    InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("1", callback_data="1"),
                InlineKeyboardButton("2", callback_data="2"),
            ],
            [
                InlineKeyboardButton("3", callback_data="3"),
                InlineKeyboardButton("4", callback_data="4"),
            ],
            [InlineKeyboardButton("Удалить слово", callback_data="5")],
        ]
    ),
)
