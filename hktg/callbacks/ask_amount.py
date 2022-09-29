
from telegram import Update
from telegram.ext import ContextTypes

from hktg.constants import UserDataKey
from hktg import dbwrapper
from hktg.util import reset_data

class AskAmount:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        user_data = context.user_data
        message = ""

        instances = dbwrapper.get_table(dbwrapper.Tables.INSTANCE)
        products = dbwrapper.get_table(dbwrapper.Tables.PRODUCT)
        locations = dbwrapper.get_table(dbwrapper.Tables.LOCATION)
        containers = dbwrapper.get_table(dbwrapper.Tables.CONTAINER)

        if user_data[UserDataKey.ACTION] == Action.MODIFY:
            if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LIMIT:
                product_name = find_in_table(
                    products, 0, user_data[UserDataKey.CURRENT_ID])
                container_symbol = find_in_table(
                    containers, 0, user_data[UserDataKey.CONTAINER])[1]
                message = LIMIT_MESSAGE % (product_name, container_symbol)

            else:
                instance = find_in_table(
                    instances, 0, user_data[UserDataKey.CURRENT_ID])
                (id, product_id, location_id, amount,
                 container, date, editor) = instance
                product_name = find_in_table(products, 0, product_id)[1]
                location_name = find_in_table(locations, 0, location_id)[1]
                container_symbol = find_in_table(
                    containers, 0, user_data[UserDataKey.CONTAINER])[1]

                message = AMOUNT_MESSAGE % (
                    container_symbol, product_name, location_name)

        elif user_data[UserDataKey.ACTION] == Action.CREATE:

            product_name = find_in_table(
                products, 0, user_data[UserDataKey.CONTAINER])[1]
            location_name = find_in_table(
                locations, 0, user_data[UserDataKey.LOCATION])[1]
            container_symbol = find_in_table(
                containers, 0, user_data[UserDataKey.CONTAINER])[1]

            message = ADD_AMOUNT_MESSAGE % (
                container_symbol, product_name, location_name)

        await update.callback_query.edit_message_text(text=message)

        return State.ENTERING_AMOUNT

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        user_data = context.user_data

        if not update.message.text.isdigit():
            return await AskAmount.ask(update, context)

        if user_data[UserDataKey.ACTION] == Action.MODIFY:
            if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LIMIT:
                dbwrapper.update_limit(
                    user_data[UserDataKey.CURRENT_ID],
                    int(update.message.text),
                    user_data[UserDataKey.CONTAINER]
                )
            else:
                dbwrapper.update_instance(
                    user_data[UserDataKey.CURRENT_ID],
                    update.message.text,
                    update.effective_user.name
                )

            return await Home.ask(update, context)

        elif user_data[UserDataKey.ACTION] == Action.CREATE:
            dbwrapper.update_instance(None, update.effective_user.name, {
                "product_id": user_data[UserDataKey.PRODUCT],
                "location_id": user_data[UserDataKey.LOCATION],
                "container_id": user_data[UserDataKey.CONTAINER],
                "amount": update.message.text,
            })
            return await Home.ask(update, context)

        else:
            logging.error("Unexpected action: %s" %
                          user_data[UserDataKey.ACTION])

        reset_data(context)

        return await Home.ask(update, context)