
from typing import Any, Dict, Tuple
from enum import Enum
import logging
import inspect
from datetime import datetime

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from . import dbwrapper


class State(Enum):
    CHOOSING_ACTION = 1
    CHOOSING_LOCATION = 2
    CHOOSING_PRODUCT = 3
    ENTERING_AMOUNT = 4
    ENTERING_LOCATION = 5
    ENTERING_PRODUCT = 6
    FILTERED_VIEW = 7
    CHOOSING_CONTAINER = 8
    ENTERING_CONTAINER_SYMBOL = 9
    ENTERING_CONTAINER_DESCRIPTION = 10

class Action(Enum):
    HOME = 1
    FILTER = 2
    ADD = 3
    REMOVE = 4
    UPDATE = 5
    EXIT = ConversationHandler.END

# userdata keys for values
class UserDataKey(Enum):
    ACTION = 1
    PRODUCT = 2
    LOCATION = 3
    CONTAINER = 4
    AMOUNT = 5
    CONTAINER_SYMBOL = 6
    FIELD_TYPE = 7
    LIMIT = 8
    CURRENT_ID = 9

ACTION_DESCRIPTIONS = {
    Action.HOME: "🏠 Додому",
    Action.FILTER: "🔍 Шукати",
    Action.ADD: "➕ Додати",
    Action.REMOVE: "➖ Видалити",
    Action.UPDATE: "🔃 Оновити",
    Action.EXIT: "🚪 Вийти",
}



SHOWING_TEXT = '''🏠 Ласкаво прошу до складу_холоду!
🌶️🧑‍🍳 Куди підемо?
🏎️😏 Або нам щось привезли?'''

COMEBACK_TEXT = '''Повертайся скоріш! Для цього використай /start

Якщо я засну - зайди на https://hk-warehouse.herokuapp.com'''

NEW_LOCATION_TEXT = "І як нове місце називається?"
NEW_PRODUCT_TEXT = "І як новий продукт називається?"
NEW_CONTAINER_SYMB_TEXT = '''І який символ у нової тари?

Одне емодзі в студію, будьте любʼязні'''
NEW_CONTAINER_DESC_TEXT = "І як нова %s тара називається?"

AMOUNT_MESSAGE = '''І скільки ж стало %s з %s в %s?
Тільки цифрами, 0 видалить запис'''
ADD_AMOUNT_MESSAGE = '''I скільки ж %s з %s зʼявилось в %s?
Тільки цифрами, 0 не внесе змін'''

FILTERED_VIEW_TEXT = '''🔍 Шукаєм в:
%s'''
LIMIT_CAPTION = "🔔 Нагадати коли: %s"
LIMIT_MESSAGE = "🔔 Нагадати за %s коли скільки буде лишатись %s? Тільки цифрами"

# common

def split_list(source:list, count:int):
    result = []
    for i in range(0, len(source), count):
        result.append(source[i:i+count])
    return result

def clear_field(key, context):

    if key in context.user_data:
        del context.user_data[key]

def reset_data(context: ContextTypes.DEFAULT_TYPE):

    for key in UserDataKey:
        clear_field(key, context)

def build_data_buttons(constraint = None, location_button = False, product_button = False):

    buttons = []

    instances = dbwrapper.get_table(dbwrapper.INSTANCE_TABLE)
    locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
    products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)
    containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)

    # for l_id, l_name in locations:
    #     new_lst = list(list(i) for match, i in it.groupby(characters_list, lambda p: p == '----') if not match)

    for ( id, product, location, amount, container,  date, editor ) in instances:
        if constraint and not constraint(product, location, amount, container, date, editor):
            continue

        location_str = find_in_table(locations, 0, location)[1]
        product_str = find_in_table(products, 0, product)
        container_str = find_in_table(containers, 0, container)

        if location_button:
            buttons.append(InlineKeyboardButton(text=str(location_str), callback_data={
                UserDataKey.ACTION: Action.FILTER,
                UserDataKey.FIELD_TYPE: UserDataKey.LOCATION,
                UserDataKey.CURRENT_ID: location
            }))

        if product_button:
            buttons.append(InlineKeyboardButton(text=str(product_str), callback_data={
                UserDataKey.ACTION: Action.FILTER,
                UserDataKey.FIELD_TYPE: UserDataKey.PRODUCT,
                UserDataKey.CURRENT_ID: product
            }))
        buttons.append(InlineKeyboardButton(text="%s %s" % (amount, container_str), callback_data={
            UserDataKey.ACTION: Action.UPDATE,
            UserDataKey.FIELD_TYPE: UserDataKey.CONTAINER,
            UserDataKey.CURRENT_ID: id
        } ))

    chunk_size = 2 * 2 # buttons count for one entry

    return split_list(buttons, chunk_size)

def action_button(action: Action, callback_data = {}):

    callback_data[ UserDataKey.ACTION ] = action
    return InlineKeyboardButton(text=ACTION_DESCRIPTIONS[action], callback_data=callback_data)

def find_in_table(table, index, comparable):
    return next((x for x in table if x[index] == comparable), None)

# ask for action
class Home:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        reset_data(context)

        users = dbwrapper.get_table(dbwrapper.TG_USERS_TABLE)
        admins = dbwrapper.get_table(dbwrapper.TG_ADMINS_TABLE)
        locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)

        is_user = find_in_table(users, 1, str(update.effective_user.id))
        is_admin = is_user and find_in_table(admins, 1, is_user[0])

        buttons = []
        if is_user:
            buttons.append([
                action_button(Action.ADD, {UserDataKey.FIELD_TYPE: UserDataKey.AMOUNT})
            ])

        buttons.append([ 
            action_button(Action.FILTER, {}),
            action_button(Action.EXIT) ],
        )

        keyboard = InlineKeyboardMarkup(buttons)

        if update.callback_query:
            await update.callback_query.edit_message_text(text=SHOWING_TEXT, reply_markup=keyboard)
        else:
            await update.message.reply_text(text=SHOWING_TEXT, reply_markup=keyboard)

        return State.CHOOSING_ACTION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        await update.callback_query.answer()
        query_data = update.callback_query.data
        for key in query_data:
            context.user_data[key] = query_data[key]

        if query_data[UserDataKey.ACTION] == Action.EXIT:
            return await Home.end(update, context)

        elif query_data[UserDataKey.ACTION] == Action.ADD:
            return await SelectLocation.ask(update, context)

        elif query_data[UserDataKey.ACTION] == Action.FILTER:
            return await SelectLocation.ask(update, context)

        elif query_data[UserDataKey.ACTION] == Action.UPDATE:

            if query_data[UserDataKey.FIELD_TYPE] == UserDataKey.CONTAINER:
                return await SelectContainer.ask(update, context)
            elif query_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
                return await select_product(update, context)
            elif query_data[UserDataKey.FIELD_TYPE] == UserDataKey.LOCATION:
                return await SelectLocation.ask(update, context)

        elif query_data[UserDataKey.ACTION] == Action.FILTER:
            return await FilteredView.ask(update, context)

    @staticmethod
    async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        await update.message.reply_text(COMEBACK_TEXT, reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    @staticmethod
    async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=COMEBACK_TEXT)

        return ConversationHandler.END

class SelectLocation:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
        buttons = []
        for location_id, location_name in locations:
            buttons.append(InlineKeyboardButton(text=location_name, callback_data=location_id))

        users = dbwrapper.get_table(dbwrapper.TG_USERS_TABLE)
        is_user = find_in_table(users, 1, str(update.effective_user.id))

        if is_user:
            buttons.append(action_button(Action.ADD))

        buttons = split_list(buttons, 2)

        keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.edit_message_text(text="Виберіть локацію:", reply_markup=keyboard)

        return State.CHOOSING_LOCATION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        await update.callback_query.answer()

        selected_location =  update.callback_query.data
        user_data = context.user_data

        action = user_data[UserDataKey.ACTION]
        if isinstance(selected_location, dict):
            return await AddLocation.ask(update, context)

        elif action == Action.UPDATE:
            if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LOCATION:
                dbwrapper.update_value(dbwrapper.INSTANCE_TABLE, {'location_id': selected_location}, {'id': user_data[UserDataKey.CURRENT_ID]})
                return await Home.ask(update, context)
        elif action == Action.ADD:
            user_data[UserDataKey.LOCATION] = selected_location
            return await SelectProduct.ask(update, context)
        elif action == Action.FILTER:
            user_data[UserDataKey.FIELD_TYPE] = UserDataKey.LOCATION
            user_data[UserDataKey.CURRENT_ID] = selected_location
            await update.callback_query.answer()
            return await FilteredView.ask(update, context)

class SelectProduct:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)

        buttons = []
        for product_id, product_name in products:
            buttons.append(InlineKeyboardButton(text=product_name, callback_data=product_id))

        users = dbwrapper.get_table(dbwrapper.TG_USERS_TABLE)
        is_user = find_in_table(users, 1, str(update.effective_user.id))

        if is_user:
            buttons.append(action_button(Action.ADD))

        buttons = split_list(buttons, 2)

        keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.edit_message_text(text="Виберіть продукцію:", reply_markup=keyboard)

        return State.CHOOSING_PRODUCT

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        selected_product =  update.callback_query.data

        if isinstance(selected_product, dict):
            return await AddProduct.ask(update, context)

        if context.user_data[UserDataKey.ACTION] == Action.UPDATE:
            if context.user_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
                dbwrapper.update_value(dbwrapper.INSTANCE_TABLE, {'product_id': selected_product}, {'id': context.user_data[UserDataKey.CURRENT_ID]})
            else:
                logging.error("Unexpected datafield %s" % context.user_data[UserDataKey.FIELD_TYPE])
            return await Home.ask(update, context)
        elif context.user_data[UserDataKey.ACTION] == Action.ADD:
            context.user_data[UserDataKey.PRODUCT] = selected_product
            return await SelectContainer.ask(update, context)

class SelectContainer:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)
        buttons = []
        for container_id, containers_symbol, containers_desc in containers:
            buttons.append(
                InlineKeyboardButton(text="%s %s" % (containers_symbol, containers_desc), callback_data=container_id),
            )

        users = dbwrapper.get_table(dbwrapper.TG_USERS_TABLE)
        is_user = find_in_table(users, 1, str(update.effective_user.id))

        if is_user:
            buttons.append(action_button(Action.ADD))

        buttons = split_list(buttons, 2)

        keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.edit_message_text(text="Виберіть тару:", reply_markup=keyboard)

        return State.CHOOSING_CONTAINER

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        selected_container =  update.callback_query.data
        user_data = context.user_data

        if isinstance(selected_container, dict):
            return await AddContainerSymbol.ask(update, context)

        if context.user_data[UserDataKey.ACTION] in (Action.ADD, Action.UPDATE):
            context.user_data[UserDataKey.CONTAINER] = selected_container
            return await AskAmount.ask(update, context)

class AskAmount:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        user_data = context.user_data
        message = ""

        instances = dbwrapper.get_table(dbwrapper.INSTANCE_TABLE)
        products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)
        locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
        containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)

        if user_data[UserDataKey.ACTION] == Action.UPDATE:
            if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LIMIT:
                product_name = find_in_table(products, 0, user_data[UserDataKey.CURRENT_ID])
                container_symbol = find_in_table(containers, 0, user_data[UserDataKey.CONTAINER])[1]
                message = LIMIT_MESSAGE % (product_name, container_symbol)

            else:
                instance = find_in_table(instances, 0, user_data[UserDataKey.CURRENT_ID])
                ( id, product_id, location_id, amount, container, date, editor ) = instance
                product_name = find_in_table(products, 0, product_id)[1]
                location_name = find_in_table(locations, 0, location_id)[1]
                container_symbol = find_in_table(containers, 0, user_data[UserDataKey.CONTAINER])[1]

                message = AMOUNT_MESSAGE % (container_symbol, product_name, location_name)

        elif user_data[UserDataKey.ACTION] == Action.ADD:

            product_name = find_in_table(products, 0, user_data[UserDataKey.CONTAINER])[1]
            location_name = find_in_table(locations, 0, user_data[UserDataKey.LOCATION])[1]
            container_symbol = find_in_table(containers, 0, user_data[UserDataKey.CONTAINER])[1]

            message = ADD_AMOUNT_MESSAGE % (container_symbol, product_name, location_name)

        await update.callback_query.edit_message_text(text=message)

        return State.ENTERING_AMOUNT

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        user_data = context.user_data

        if not update.message.text.isdigit():
            return await AskAmount.ask(update, context)

        if user_data[UserDataKey.ACTION] == Action.UPDATE:
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

        elif user_data[UserDataKey.ACTION] == Action.ADD:
            dbwrapper.update_instance(None, update.effective_user.name, {
                "product_id": user_data[UserDataKey.PRODUCT],
                "location_id": user_data[UserDataKey.LOCATION],
                "container_id": user_data[UserDataKey.CONTAINER],
                "amount": update.message.text,
            })
            return await Home.ask(update, context)

        else:
            logging.error("Unexpected action: %s" % user_data[UserDataKey.ACTION])


        reset_data(context)

        return await Home.ask(update, context)

class AddContainerSymbol:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=NEW_CONTAINER_SYMB_TEXT)

        return State.ENTERING_CONTAINER_SYMBOL

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        user_data = context.user_data

        if user_data[UserDataKey.ACTION] == Action.UPDATE:
            dbwrapper.update_value(dbwrapper.CONTAINER_TABLE,
                {
                    'amount': update.message.text,
                    "date": datetime.now(),
                    "editor": update.effective_user.name,
                },
                {'id': user_data[UserDataKey.CURRENT_ID]}
            )
            return await Home.ask(update, context)

        elif user_data[UserDataKey.ACTION] == Action.ADD:
            user_data[UserDataKey.CONTAINER_SYMBOL] = update.message.text
            return await AddContainerDescription.ask(update, context)
        
        else:
            logging.error("Unexpected action: %s" % user_data[UserDataKey.ACTION])

class AddContainerDescription:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)
        user_data = context.user_data

        message = NEW_CONTAINER_DESC_TEXT % user_data[UserDataKey.CONTAINER_SYMBOL]

        if update.callback_query:
            await update.callback_query.edit_message_text(text=message)
        else:
            await update.message.reply_text(text=message)

        return State.ENTERING_CONTAINER_DESCRIPTION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)
        user_data = context.user_data

        dbwrapper.insert_value(dbwrapper.CONTAINER_TABLE, {
            "description": update.message.text,
            "symbol": user_data[UserDataKey.CONTAINER_SYMBOL]
        })

        return await Home.ask(update, context)

class AddLocation:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=NEW_LOCATION_TEXT)

        return State.ENTERING_LOCATION

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        logging.info(inspect.stack()[0][0].f_code.co_name)

        dbwrapper.insert_value(dbwrapper.LOCATION_TABLE, {"name": update.message.text})
        # update.get_bot().send_message(chat_id, text)
        return await Home.ask(update, context)

class AddProduct:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=NEW_PRODUCT_TEXT)

        return State.ENTERING_PRODUCT

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        dbwrapper.insert_value(dbwrapper.PRODUCT_TABLE, {"name": update.message.text})
        return await Home.ask(update, context)

class FilteredView:
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        logging.info(inspect.stack()[0][0].f_code.co_name)

        await update.callback_query.answer()

        user_data = context.user_data

        def constraint(product, location, amount, container, date, editor):
            if UserDataKey.FIELD_TYPE in user_data:
                if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
                    return product == user_data[UserDataKey.CURRENT_ID]
                if user_data[UserDataKey.FIELD_TYPE] ==  UserDataKey.LOCATION:
                    return location == user_data[UserDataKey.CURRENT_ID]
                logging.warning("unexpected filter")
            return True

        buttons = build_data_buttons(
            constraint,
            user_data[UserDataKey.FIELD_TYPE] != UserDataKey.LOCATION,
            user_data[UserDataKey.FIELD_TYPE] != UserDataKey.PRODUCT
        )
        extra_buttons = []
        if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
            limits = dbwrapper.get_table(dbwrapper.LIMIT_TABLE)
            
            limit = find_in_table(limits, 1, query_data[UserDataKey.CURRENT_ID])
            limit_str = "ніколи"

            if limit:
                containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)
                limit = find_in_table(containers, 0, limit[3])
                limit_str = "%s %s" % (limit[2], container[1])

            extra_buttons.append(
                InlineKeyboardButton(text=LIMIT_CAPTION % limit_str, callback_data={
                        UserDataKey.ACTION: Action.UPDATE,
                        UserDataKey.FIELD_TYPE: UserDataKey.LIMIT
                    }),
            )
        
        extra_buttons.append(
            InlineKeyboardButton(text=ACTION_DESCRIPTIONS[Action.HOME], callback_data={
                    UserDataKey.ACTION: Action.HOME
                }),
        )

        buttons.append(extra_buttons)

        keyboard = InlineKeyboardMarkup(buttons)

        message = ""
        if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
            products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)
            product_str =  find_in_table(products, 0, user_data[UserDataKey.CURRENT_ID])[1]
            message = FILTERED_VIEW_TEXT % product_str

        elif user_data[UserDataKey.FIELD_TYPE] ==  UserDataKey.LOCATION:
            locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
            location_str =  find_in_table(locations, 0, user_data[UserDataKey.CURRENT_ID])[1]
            message = FILTERED_VIEW_TEXT % location_str

        await update.callback_query.edit_message_text(text=message, reply_markup=keyboard)

        return State.FILTERED_VIEW

    @staticmethod
    async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

        logging.info(inspect.stack()[0][0].f_code.co_name)

        # await update.callback_query.answer()
        query_data = update.callback_query.data

        if query_data[UserDataKey.ACTION] == Action.FILTER:
            return await FilteredView.ask(update, context)

        elif query_data[UserDataKey.ACTION] == Action.UPDATE:
            for key in query_data:
                context.user_data[key] = query_data[key]
            return await SelectContainer.ask(update, context)

        return await Home.ask(update, context)

# getter

def get_handler():


    return ConversationHandler(
        entry_points=[CommandHandler("start", Home.ask)],

        # exit state -> handler
        states={
            State.CHOOSING_ACTION: [ CallbackQueryHandler(Home.answer) ],
            State.CHOOSING_LOCATION: [ CallbackQueryHandler(SelectLocation.answer) ],
            State.CHOOSING_PRODUCT: [ CallbackQueryHandler(SelectProduct.answer) ],
            State.CHOOSING_CONTAINER: [ CallbackQueryHandler(SelectContainer.answer) ],
            State.ENTERING_LOCATION: [ MessageHandler( filters.TEXT & ~filters.COMMAND, AddLocation.answer ) ],
            State.ENTERING_PRODUCT: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, AddProduct.answer )
            ],
            State.ENTERING_CONTAINER_SYMBOL: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, AddContainerSymbol.answer )
            ],
            State.ENTERING_CONTAINER_DESCRIPTION: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, AddContainerDescription.answer )
            ],
            State.ENTERING_AMOUNT: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, AskAmount.answer )
            ],
            State.FILTERED_VIEW: [ CallbackQueryHandler(FilteredView.answer) ],
        },
        fallbacks=[
            CommandHandler("stop", Home.stop),
            CallbackQueryHandler(Home.stop, pattern="^" + str(ConversationHandler.END) + "$")
        ],
        allow_reentry=True
    )

