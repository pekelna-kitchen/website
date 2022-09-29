

from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import UserDataKey
from hktg import dbwrapper, callbacks
from hktg.constants import (
    Action,
    State,
    UserDataKey
)

class AddContainerSymbol:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=NEW_CONTAINER_SYMB_TEXT)

        return State.ENTERING_CONTAINER_SYMBOL

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        user_data = context.user_data

        if user_data[UserDataKey.ACTION] == Action.MODIFY:
            dbwrapper.update_value(dbwrapper.Tables.CONTAINER,
                                   {
                                       'amount': update.message.text,
                                       "date": datetime.now(),
                                       "editor": update.effective_user.name,
                                   },
                                   {'id': user_data[UserDataKey.CURRENT_ID]}
                                   )
            return await callbacks.Home.ask(update, context)

        elif user_data[UserDataKey.ACTION] == Action.CREATE:
            user_data[UserDataKey.CONTAINER_SYMBOL] = update.message.text
            return await callbacks.AddContainerDescription.ask(update, context)

        else:
            logging.error("Unexpected action: %s" %
                          user_data[UserDataKey.ACTION])

