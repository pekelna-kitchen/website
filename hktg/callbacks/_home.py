
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import (
    Action,
    UserDataKey,
    State
)
from hktg import dbwrapper, util, callbacks

from hktg.strings import SHOWING_TEXT, COMEBACK_TEXT

class Home:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        
        from telegram import InlineKeyboardMarkup

        util.reset_data(context)

        # users = dbwrapper.get_table(dbwrapper.Tables.TG_USERS)
        admins = dbwrapper.get_table(dbwrapper.Tables.TG_ADMINS)
        locations = dbwrapper.get_table(dbwrapper.Tables.LOCATION)

        is_user = util.find_in_table(dbwrapper.Tables.TG_USERS, 1, str(update.effective_user.id))
        is_admin = is_user and util.find_in_table(dbwrapper.Tables.TG_ADMINS, 1, is_user[0])

        buttons = []
        if is_user:
            buttons.append(util.action_button(Action.CREATE, {}))

        buttons.append(util.action_button(Action.FILTER, {}))
        buttons.append(util.action_button(Action.EXIT, {}))

        keyboard = InlineKeyboardMarkup([buttons])

        if update.callback_query:
            await update.callback_query.edit_message_text(text=SHOWING_TEXT, reply_markup=keyboard)
        else:
            await update.message.reply_text(text=SHOWING_TEXT, reply_markup=keyboard)

        return State.CHOOSING_ACTION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        query_data = update.callback_query.data
        for key in query_data:
            context.user_data[key] = query_data[key]

        action_mapping = {
            Action.EXIT: callbacks.Home.stop,
            Action.CREATE: callbacks.ViewEntry.ask,
            Action.FILTER: callbacks.FilteredView.ask
        }

        return await action_mapping[query_data[UserDataKey.ACTION]](update, context)

    @staticmethod
    async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        from telegram import ReplyKeyboardRemove

        util.reset_data(context)

        if update.callback_query:
            await update.callback_query.edit_message_text(text=SHOWING_TEXT, reply_markup=keyboard)
        else:
            await update.message.reply_text(text=COMEBACK_TEXT, reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END
