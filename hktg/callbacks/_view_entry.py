
from telegram import Update
from telegram.ext import ContextTypes

import humanize
from datetime import datetime

from hktg.constants import (
    Action,
    UserDataKey,
    State
)
from hktg import dbwrapper, util, callbacks
from hktg.strings import ENTRY_MESSAGE

class ViewEntry:

    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        query_data = update.callback_query.data

        id = product_id = amount = date = editor = instance = None
        product_name = location_name = container = None

        if UserDataKey.CURRENT_ID in query_data:
            instance = util.find_in_table(dbwrapper.Tables.INSTANCE, 0, query_data[UserDataKey.CURRENT_ID])
            (id, product_id, location_id, amount, container_id, date, editor) = instance

            product_name = util.find_in_table(dbwrapper.Tables.PRODUCT, 0, product_id)[1]
            location_name = util.find_in_table(dbwrapper.Tables.LOCATION, 0, location_id)[1]
            container = util.find_in_table(dbwrapper.Tables.CONTAINER, 0, container_id)

        if not instance:
            if UserDataKey.PRODUCT in context.user_data:
                product_id = util.find_in_table(dbwrapper.Tables.PRODUCT, 0, product_id)[1]
            if UserDataKey.PRODUCT in context.user_data:
                location_name = util.find_in_table(dbwrapper.Tables.PRODUCT, 0, product_id)[1]

        product_name = util.find_in_table(dbwrapper.Tables.PRODUCT, 0, product_id)[1] if product_id else None

        amount_tuple = (amount, container[1] if container else None)

        buttons = [[
            InlineKeyboardButton(
                text="%s %s" % amount_tuple if amount else "ADD",
                callback_data={
                    UserDataKey.ACTION: Action.MODIFY,
                    UserDataKey.FIELD_TYPE: UserDataKey.AMOUNT
                }
            ),
            InlineKeyboardButton(
                text=product_name,
                callback_data={
                    UserDataKey.ACTION: Action.FILTER if id else Action.CREATE,
                    UserDataKey.FIELD_TYPE: UserDataKey.PRODUCT
                }
            ),
            InlineKeyboardButton(
                text=location_name,
                callback_data={
                    UserDataKey.ACTION: Action.MODIFY,
                    UserDataKey.FIELD_TYPE: UserDataKey.LOCATION
                }
            ),
        ]]
        buttons.append([
            util.action_button(Action.BACK),
            util.action_button(Action.HOME),
        ])
        keyboard = InlineKeyboardMarkup(buttons)

        editor_tuple = (editor, humanize.naturalday(date)) if editor else ('ніхто', 'ніколи')

        if update.callback_query:
            await update.callback_query.edit_message_text(text=ENTRY_MESSAGE % editor_tuple, reply_markup=keyboard)
        else:
            await update.message.reply_text(text=ENTRY_MESSAGE % editor_tuple, reply_markup=keyboard)

        return State.VIEWING_ENTRY

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        await update.callback_query.answer()

        query_data = update.callback_query.data
        user_data = context.user_data

        if user_data[UserDataKey.ACTION] == Action.CREATE:
            dbwrapper.update_instance(None, update.effective_user.name, {
                "product_id": user_data[UserDataKey.PRODUCT],
                "location_id": user_data[UserDataKey.LOCATION],
                "container_id": user_data[UserDataKey.CONTAINER],
                "amount": update.message.text,
            })
            util.reset_data(context)
            return await callbacks.FilteredView.ask(update, context)

        query_data = update.callback_query.data
        for key in query_data:
            context.user_data[key] = query_data[key]

        mappings = {
            Action.BACK: callbacks.FilteredView.ask,
            Action.FILTER: callbacks.FilteredView.ask,
            Action.MODIFY: callbacks.ViewAmount.ask
        }

        return await mappings[ query_data[ UserDataKey.ACTION ] ](update, context)
