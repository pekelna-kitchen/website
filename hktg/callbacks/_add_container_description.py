
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import (
    State,
    UserDataKey
)
from hktg import dbwrapper, callbacks

class AddContainerDescription:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        user_data = context.user_data

        message = NEW_CONTAINER_DESC_TEXT % user_data[UserDataKey.CONTAINER_SYMBOL]

        if update.callback_query:
            await update.callback_query.edit_message_text(text=message)
        else:
            await update.message.reply_text(text=message)

        return State.ENTERING_CONTAINER_DESCRIPTION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        user_data = context.user_data

        dbwrapper.insert_value(dbwrapper.Tables.CONTAINER, {
            "description": update.message.text,
            "symbol": user_data[UserDataKey.CONTAINER_SYMBOL]
        })

        return await callbacks.Home.ask(update, context)
