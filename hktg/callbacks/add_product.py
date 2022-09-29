
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import UserDataKey
from hktg import dbwrapper

class AddProduct:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=NEW_PRODUCT_TEXT)

        return State.ENTERING_PRODUCT

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        dbwrapper.insert_value(dbwrapper.Tables.PRODUCT, {
                               "name": update.message.text})
        return await Home.ask(update, context)
