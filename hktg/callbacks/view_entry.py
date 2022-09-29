
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import UserDataKey
from hktg import dbwrapper

class ViewEntry:

    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        query_data = update.callback_query.data

        instance = find_in_table(dbwrapper.INSTANCE_TABLE, 0, query_data[UserDataKey.CURRENT_ID])
        (id, product_id, location_id, amount, container, date, editor) = instance

        product_name = find_in_table(dbwrapper.PRODUCT_TABLE, 0, product_id)[1]
        location_name = find_in_table(dbwrapper.LOCATION_TABLE, 0, location_id)[1]
        container_symbol = find_in_table(dbwrapper.CONTAINER_TABLE, 0, container)[1]

        buttons = [[
            InlineKeyboardButton(
                text="%s %s" % (amount, container_symbol),
                callback_data={
                    UserDataKey.ACTION: Action.MODIFY,
                    UserDataKey.CURRENT_ID: id,
                    UserDataKey.FIELD_TYPE: UserDataKey.AMOUNT
                }
            ),
            InlineKeyboardButton(
                text=product_name,
                callback_data={
                    UserDataKey.ACTION: Action.FILTER,
                    UserDataKey.CURRENT_ID: product_id,
                    UserDataKey.FIELD_TYPE: UserDataKey.PRODUCT
                }
            ),
            InlineKeyboardButton(
                text=location_name,
                callback_data={
                    UserDataKey.ACTION: Action.FILTER,
                    UserDataKey.CURRENT_ID: location_id,
                    UserDataKey.FIELD_TYPE: UserDataKey.LOCATION
                }
            ),
        ]]
        keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.edit_message_text(text=ENTRY_MESSAGE % (editor, date), reply_markup=keyboard)

        return State.VIEWING_ENTRY

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        return await Home.ask(update, context)

