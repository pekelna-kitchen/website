
from enum import Enum


class State(Enum):
    CHOOSING_ACTION = 1
    CHOOSING_LOCATION = 2
    CHOOSING_PRODUCT = 3
    ENTERING_AMOUNT = 4
    ENTERING_LOCATION = 5
    ENTERING_PRODUCT = 6
    FILTERED_VIEW = 7
    CHOOSING_CONTAINER = 8
    ENTERING_CONTAINER_SYMBOL = 9
    ENTERING_CONTAINER_DESCRIPTION = 10
    VIEWING_ENTRY = 11


class Action(Enum):
    HOME = 1
    FILTER = 2
    CREATE = 3
    DELETE = 4
    MODIFY = 5
    VIEW_ENTRY = 5
    EXIT = 6

# userdata keys for values


class UserDataKey(Enum):
    ACTION = 1
    PRODUCT = 2
    LOCATION = 3
    CONTAINER = 4
    AMOUNT = 5
    CONTAINER_SYMBOL = 6
    FIELD_TYPE = 7
    LIMIT = 8
    CURRENT_ID = 9


ActionDescriptions = {
    Action.HOME: "🏠 Додому",
    Action.FILTER: "🔍 Шукати",
    Action.CREATE: "➕ Додати",
    Action.DELETE: "➖ Видалити",
    Action.MODIFY: "🖊️ Змінити",
    Action.EXIT: "🚪 Вийти",
}


SHOWING_TEXT = '''🏠 Ласкаво прошу до складу_холоду!
🌶️🧑‍🍳 Куди підемо?
🏎️😏 Або нам щось привезли?'''

COMEBACK_TEXT = '''Повертайся скоріш! Для цього використай /start

Якщо я засну - зайди на https://hk-warehouse.herokuapp.com'''

NEW_LOCATION_TEXT = "І як нове місце називається?"
NEW_PRODUCT_TEXT = "І як новий продукт називається?"
NEW_CONTAINER_SYMB_TEXT = '''І який символ у нової тари?

Одне емодзі в студію, будьте любʼязні'''
NEW_CONTAINER_DESC_TEXT = "І як нова %s тара називається?"

AMOUNT_MESSAGE = '''І скільки ж стало %s з %s в %s?
Тільки цифрами, 0 видалить запис'''
ADD_AMOUNT_MESSAGE = '''I скільки ж %s з %s зʼявилось в %s?
Тільки цифрами, 0 не внесе змін'''

FILTERED_VIEW_TEXT = '''🔍 Шукаєм в:
%s'''
LIMIT_CAPTION = "🔔 Нагадати коли: %s"
LIMIT_MESSAGE = "🔔 Нагадати за %s коли скільки буде лишатись %s? Тільки цифрами"
ENTRY_MESSAGE = ''' Цей запис зробив %s %s'''
