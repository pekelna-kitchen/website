
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import (
    Action,
    State,
    UserDataKey
)
from hktg import dbwrapper, util, callbacks
from hktg.strings import SELECT_LOCATION_TEXT

class SelectLocation:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        locations = dbwrapper.get_table(dbwrapper.Tables.LOCATION)

        buttons = []
        for id, name in locations:
            buttons.append(InlineKeyboardButton(text=name, callback_data=id))

        users = dbwrapper.get_table(dbwrapper.Tables.TG_USERS)
        is_user = util.find_in_table(users, 1, str(update.effective_user.id))

        if is_user:
            buttons.append(util.action_button(Action.CREATE))

        buttons = util.split_list(buttons, 2)

        keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.edit_message_text(text=SELECT_LOCATION_TEXT, reply_markup=keyboard)

        return State.CHOOSING_LOCATION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        selected_product = update.callback_query.data
        user_data = context.user_data

        if isinstance(selected_product, dict):
            return await callbacks.AddProduct.ask(update, context)

        if context.user_data[UserDataKey.ACTION] == Action.MODIFY:
            if context.user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LOCATION:
                dbwrapper.update_value(dbwrapper.Tables.INSTANCE, {
                    'location_id': selected_location
                }, {
                    'id': context.user_data[UserDataKey.CURRENT_ID]
                })
            else:
                logging.error("Unexpected datafield %s" %
                              context.user_data[UserDataKey.FIELD_TYPE])
            return await callbacks.Home.ask(update, context)
        elif context.user_data[UserDataKey.ACTION] == Action.CREATE:
            context.user_data[UserDataKey.PRODUCT] = selected_product
            return await callbacks.SelectContainer.ask(update, context)

