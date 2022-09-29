
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import (
    Action,
    State,
    UserDataKey
)
from hktg import dbwrapper, util, callbacks

class SelectContainer:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        containers = dbwrapper.get_table(dbwrapper.Tables.CONTAINER)
        buttons = []
        for container_id, containers_symbol, containers_desc in containers:
            buttons.append(
                InlineKeyboardButton(text="%s %s" % (
                    containers_symbol, containers_desc), callback_data=container_id),
            )

        is_user = util.find_in_table(dbwrapper.Tables.TG_USERS, 1, str(update.effective_user.id))

        if is_user:
            buttons.append(util.action_button(Action.CREATE, {}))

        buttons = util.split_list(buttons, 2)

        keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.edit_message_text(text="Виберіть тару:", reply_markup=keyboard)

        return State.CHOOSING_CONTAINER

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        selected_container = update.callback_query.data
        user_data = context.user_data

        if isinstance(selected_container, dict):
            return await callbacks.AddContainerSymbol.ask(update, context)

        if context.user_data[UserDataKey.ACTION] in (Action.CREATE, Action.MODIFY):
            context.user_data[UserDataKey.CONTAINER] = selected_container
            return await callbacks.AskAmount.ask(update, context)

