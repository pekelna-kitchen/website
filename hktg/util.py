
from telegram import Update
from telegram.ext import ContextTypes

from .constants import (
    UserDataKey,
    Action,
    ActionDescriptions
)

def split_list(source: list, count: int):
    result = []
    for i in range(0, len(source), count):
        result.append(source[i:i+count])
    return result


def clear_field(key, context):

    if key in context.user_data:
        del context.user_data[key]


def reset_data(context: ContextTypes.DEFAULT_TYPE):

    for key in UserDataKey:
        clear_field(key, context)


def action_button(action: Action, callback_data={}):

    callback_data[UserDataKey.ACTION] = action
    return InlineKeyboardButton(text=ActionDescriptions[action], callback_data=callback_data)


def find_in_table(table_name, index, comparable):

    from hktg.dbwrapper import get_table

    table = get_table(table_name)
    return next((x for x in table if x[index] == comparable), None)
