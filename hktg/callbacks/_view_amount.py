
from telegram import Update
from telegram.ext import ContextTypes

import humanize

from hktg.constants import (
    Action,
    UserDataKey,
    State
)
from hktg import dbwrapper, util, callbacks
from hktg.strings import ENTRY_MESSAGE

class ViewAmount:

    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        query_data = update.callback_query.data
        user_data = context.user_data

        instance = util.find_in_table(dbwrapper.Tables.INSTANCE, 0, user_data[UserDataKey.CURRENT_ID])
        (id, product_id, location_id, amount, container, date, editor) = instance

        product_name = util.find_in_table(dbwrapper.Tables.PRODUCT, 0, product_id)[1]
        location_name = util.find_in_table(dbwrapper.Tables.LOCATION, 0, location_id)[1]
        container_symbol = util.find_in_table(dbwrapper.Tables.CONTAINER, 0, container)[1]

        buttons = [[
            InlineKeyboardButton(
                text=amount,
                callback_data={
                    UserDataKey.ACTION: Action.MODIFY,
                    UserDataKey.FIELD_TYPE: UserDataKey.AMOUNT,
                }
            ),
            InlineKeyboardButton(
                text=container_symbol,
                callback_data={
                    UserDataKey.ACTION: Action.MODIFY,
                    UserDataKey.FIELD_TYPE: UserDataKey.CONTAINER,
                }
            ),
            util.action_button(Action.BACK)
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

        editor_tuple = (editor, humanize.naturalday(date)) if editor else ("ніхто", "ніколи")
        await update.callback_query.edit_message_text(
            text=ENTRY_MESSAGE % editor_tuple if editor else ('ніхто', 'ніколи'),
            reply_markup=keyboard
        )

        return State.VIEWING_ENTRY

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        query_data = update.callback_query.data
        for key in query_data:
            context.user_data[key] = query_data[key]

        modify_mappings = {
            UserDataKey.CONTAINER: callbacks.SelectContainer.ask,
            UserDataKey.AMOUNT: callbacks.AskAmount.ask,
        }

        mappings = {
            Action.BACK: callbacks.ViewEntry.ask,
            Action.FILTER: callbacks.FilteredView.ask,
            Action.MODIFY: lambda u, c: modify_mappings[query_data[UserDataKey.FIELD_TYPE]](u, c)
        }

        return await mappings[ query_data[ UserDataKey.ACTION ] ](update, context)
