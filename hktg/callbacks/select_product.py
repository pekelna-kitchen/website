
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import UserDataKey
from hktg import dbwrapper
from hktg.util import (
    split_list, 
    action_button
)



class SelectProduct:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)

        buttons = []
        for product_id, product_name in products:
            buttons.append(InlineKeyboardButton(
                text=product_name, callback_data=product_id))

        users = dbwrapper.get_table(dbwrapper.TG_USERS_TABLE)
        is_user = find_in_table(users, 1, str(update.effective_user.id))

        if is_user:
            buttons.append(action_button(Action.CREATE))

        buttons = split_list(buttons, 2)

        keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.edit_message_text(text="Виберіть продукцію:", reply_markup=keyboard)

        return State.CHOOSING_PRODUCT

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        selected_product = update.callback_query.data

        if isinstance(selected_product, dict):
            return await AddProduct.ask(update, context)

        if context.user_data[UserDataKey.ACTION] == Action.MODIFY:
            if context.user_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
                dbwrapper.update_value(dbwrapper.INSTANCE_TABLE, {'product_id': selected_product}, {
                                       'id': context.user_data[UserDataKey.CURRENT_ID]})
            else:
                logging.error("Unexpected datafield %s" %
                              context.user_data[UserDataKey.FIELD_TYPE])
            return await Home.ask(update, context)
        elif context.user_data[UserDataKey.ACTION] == Action.CREATE:
            context.user_data[UserDataKey.PRODUCT] = selected_product
            return await SelectContainer.ask(update, context)

