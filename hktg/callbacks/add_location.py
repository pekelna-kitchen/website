
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import UserDataKey
from hktg import dbwrapper


class AddLocation:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=NEW_LOCATION_TEXT)

        return State.ENTERING_LOCATION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        dbwrapper.insert_value(dbwrapper.Tables.LOCATION, {
                               "name": update.message.text})
        # update.get_bot().send_message(chat_id, text)
        return await Home.ask(update, context)

