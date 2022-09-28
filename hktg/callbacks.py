
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
    SHOW = 1
    ADD = 2
    REMOVE = 3
    UPDATE = 4
    FILTER = 5
    DONE = ConversationHandler.END

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

ACTION_DESCRIPTIONS = {
    Action.SHOW: "🔍 Показати",
    Action.ADD: "➕ Додати",
    Action.REMOVE: "Видалити",
    Action.UPDATE: "Оновити",
    Action.DONE: "Готово",
    # Action.FILTER: "Фільтр",
}

COMEBACK_TEXT = "Повертайся скоріш! Для цього використай /start"
NEW_LOCATION_TEXT = "І як нове місце називається?"
NEW_PRODUCT_TEXT = "І як новий продукт називається?"
NEW_CONTAINER_SYMB_TEXT = "І який символ у нової тари? Одне емодзі"
NEW_CONTAINER_DESC_TEXT = "І як нова %s тара називається?"
AMOUNT_MESSAGE = "І скільки ж стало %s з %s в %s? Тільки цифрами, 0 видалить запис"
ADD_AMOUNT_MESSAGE = "I скільки ж %s з %s зʼявилось в %s?  Тільки цифрами, 0 не внесе змін"
SHOWING_TEXT = "🏠 Ласкаво просимо до складу!\nЯкщо я засну - зайдіть на https://hk-warehouse.herokuapp.com\nОсь що в нас є:"
FILTERED_VIEW_TEXT = "🔍 Шукаєм %s:"
LIMIT_CAPTION = "Нагадати коли: %s"
LIMIT_MESSAGE = "Нагадати за %s коли скільки буде лишатись %s? Тільки цифрами"

# TODO
# REMOVE_CAPTION = "❌"

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

def build_data_buttons(constraint = None):

    buttons = []

    instances = dbwrapper.get_table(dbwrapper.INSTANCE_TABLE)
    locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
    products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)
    containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)

    # for l_id, l_name in locations:
    # InlineKeyboardButton(text=str(location_str), callback_data={
    #     UserDataKey.ACTION: Action.FILTER,
    #     UserDataKey.FIELD_TYPE: UserDataKey.LOCATION,
    #     'data': location
    # }),
    #     new_lst = list(list(i) for match, i in it.groupby(characters_list, lambda p: p == '----') if not match)

    for ( id, product, location, amount, container,  date, editor ) in instances:
        if constraint and not constraint(product, location, amount, container, date, editor):
            continue

        location_str = next((x for x in locations if x[0] == location), None)[1]
        product_str = next((x for x in products if x[0] == product), None)[1]
        container_str = next((x for x in containers if x[0] == container), None)[1]

        buttons.append(InlineKeyboardButton(text=str(product_str), callback_data={
            UserDataKey.ACTION: Action.FILTER,
            UserDataKey.FIELD_TYPE: UserDataKey.PRODUCT,
            'data': product
        }))
        buttons.append(InlineKeyboardButton(text="%s %s" % (amount, container_str), callback_data={
            UserDataKey.ACTION: Action.UPDATE,
            UserDataKey.FIELD_TYPE: UserDataKey.CONTAINER,
            'data': id
        } ))

    chunk_size = 2 * 2 # buttons count for one entry

    return split_list(buttons, chunk_size)

# ask for action
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    buttons = []

    locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
    for l_id, l_name in locations:
        buttons.append([
            InlineKeyboardButton(text=str(l_name), callback_data={
                UserDataKey.ACTION: Action.FILTER,
                UserDataKey.FIELD_TYPE: UserDataKey.LOCATION,
                'data': l_id
            }),
        ])

    buttons.append([
        InlineKeyboardButton(text=ACTION_DESCRIPTIONS[Action.ADD], callback_data={
                UserDataKey.ACTION: Action.ADD,
                UserDataKey.FIELD_TYPE: UserDataKey.CONTAINER
            }),
        InlineKeyboardButton(text=ACTION_DESCRIPTIONS[Action.DONE], callback_data={
                UserDataKey.ACTION: ConversationHandler.END
            }),
    ])

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.edit_message_text(text=SHOWING_TEXT, reply_markup=keyboard)
    else:
        await update.message.reply_text(text=SHOWING_TEXT, reply_markup=keyboard)

    return State.CHOOSING_ACTION

async def on_storage_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    query_data = update.callback_query.data
    for key in query_data:
        context.user_data[key] = query_data[key]

    if query_data[UserDataKey.ACTION] == ConversationHandler.END:
        return await end(update, context)

    elif query_data[UserDataKey.ACTION] == Action.ADD:

        await select_location(update, context)
        return State.CHOOSING_LOCATION

    elif query_data[UserDataKey.ACTION] == Action.SHOW:

        await select_location(update, context)
        return State.CHOOSING_LOCATION

    elif query_data[UserDataKey.ACTION] == Action.UPDATE:

        if query_data[UserDataKey.FIELD_TYPE] == UserDataKey.CONTAINER:
            await select_container(update, context)
            return State.CHOOSING_CONTAINER
        elif query_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
            await select_product(update, context)
            return State.CHOOSING_PRODUCT
        elif query_data[UserDataKey.FIELD_TYPE] == UserDataKey.LOCATION:
            await select_location(update, context)
            return State.CHOOSING_LOCATION

    elif query_data[UserDataKey.ACTION] == Action.FILTER:
        await filtered_view(update, context)
        return State.FILTERED_VIEW


async def select_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
    buttons = []
    for location_id, location_name in locations:
        buttons.append(InlineKeyboardButton(text=location_name, callback_data=location_id))

    buttons.append(InlineKeyboardButton(text=ACTION_DESCRIPTIONS[ Action.ADD ], callback_data={
        "action": Action.ADD
    }))

    buttons = split_list(buttons, 2)

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text="Виберіть локацію:", reply_markup=keyboard)

    return State.CHOOSING_LOCATION

async def on_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.callback_query.answer()

    selected_location =  update.callback_query.data

    if isinstance(selected_location, dict):
        return await add_location(update, context)

    elif context.user_data[UserDataKey.ACTION] == Action.UPDATE:
        if context.user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LOCATION:
            dbwrapper.update_value(dbwrapper.INSTANCE_TABLE, {'location_id': selected_location}, {'id': context.user_data['data']})
            return await start(update, context)
    elif context.user_data[UserDataKey.ACTION] == Action.ADD:
        context.user_data[UserDataKey.LOCATION] = selected_location
        return await select_product(update, context)


async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)

    buttons = []
    for product_id, product_name in products:
        buttons.append(InlineKeyboardButton(text=product_name, callback_data=product_id))

    buttons.append(
        InlineKeyboardButton(text=ACTION_DESCRIPTIONS[ Action.ADD ], callback_data={
            "action": Action.ADD
        })
    )

    buttons = split_list(buttons, 2)

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text="Виберіть продукцію:", reply_markup=keyboard)

    return State.CHOOSING_PRODUCT

async def on_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    selected_product =  update.callback_query.data

    if isinstance(selected_product, dict):
        return await add_product(update, context)

    if context.user_data[UserDataKey.ACTION] == Action.UPDATE:
        if context.user_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
            dbwrapper.update_value(dbwrapper.INSTANCE_TABLE, {'product_id': selected_product}, {'id': context.user_data['data']})
            return await start(update, context)
    elif context.user_data[UserDataKey.ACTION] == Action.ADD:
        context.user_data[UserDataKey.PRODUCT] = selected_product
        return await select_container(update, context)

async def select_container(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)
    buttons = []
    for container_id, containers_symbol, containers_desc in containers:
        buttons.append(
            InlineKeyboardButton(text="%s %s" % (containers_symbol, containers_desc), callback_data=container_id),
        )

    buttons.append(InlineKeyboardButton(text=ACTION_DESCRIPTIONS[ Action.ADD ], callback_data={
        "action": Action.ADD
    }))

    buttons = split_list(buttons, 2)

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text="Виберіть тару:", reply_markup=keyboard)

    return State.CHOOSING_CONTAINER

async def on_container(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    selected_container =  update.callback_query.data
    user_data = context.user_data

    if isinstance(selected_container, dict):
        return await add_container(update, context)

    if context.user_data[UserDataKey.ACTION] in (Action.ADD, Action.UPDATE):
        context.user_data[UserDataKey.CONTAINER] = selected_container
        return await ask_amount(update, context)


async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    user_data = context.user_data
    message = ""

    instances = dbwrapper.get_table(dbwrapper.INSTANCE_TABLE)
    products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)
    locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
    containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)

    if user_data[UserDataKey.ACTION] == Action.UPDATE:

        if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LIMIT:
            product_name = next((x for x in products if x[0] == user_data['data']), None)[1]
            container_symbol = next((x for x in containers if x[0] == user_data[UserDataKey.CONTAINER]), None)[1]
            message = LIMIT_MESSAGE % (product_name, container_symbol)
        else:
            instance = next((x for x in instances if x[0] == user_data['data']), None)
            ( id, product_id, location_id, amount, container, date, editor ) = instance
            product_name = next((x for x in products if x[0] == product_id), None)[1]
            location_name = next((x for x in locations if x[0] == location_id), None)[1]
            container_symbol = next((x for x in containers if x[0] == user_data[UserDataKey.CONTAINER]), None)[1]

            message = AMOUNT_MESSAGE % (container_symbol, product_name, location_name)

    elif user_data[UserDataKey.ACTION] == Action.ADD:

        product_name = next((x for x in products if x[0] == user_data[UserDataKey.PRODUCT]), None)[1]
        location_name = next((x for x in locations if x[0] ==  user_data[UserDataKey.LOCATION]), None)[1]
        container_symbol = next((x for x in containers if x[0] == user_data[UserDataKey.CONTAINER]), None)[1]

        message = ADD_AMOUNT_MESSAGE % (container_symbol, product_name, location_name)

    await update.callback_query.edit_message_text(text=message)

    return State.ENTERING_AMOUNT

async def on_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    user_data = context.user_data

    if not update.message.text.isdigit():
        return await ask_amount(update, context)

    if user_data[UserDataKey.ACTION] == Action.UPDATE:
        if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LIMIT:

            if int(update.message.text) == 0:
                dbwrapper.delete_value(dbwrapper.LIMIT_TABLE, {'product': user_data['data']})
            else:
                limits = dbwrapper.get_table(dbwrapper.LIMIT_TABLE)
                limit = next((x for x in limits if x[0] == query_data['data']), None)

                if limit:
                    dbwrapper.update_value(dbwrapper.LIMIT_TABLE,
                        {
                            'amount': update.message.text,
                            "container_id": user_data[UserDataKey.CONTAINER],
                            "product_id": user_data['data']
                        },
                        {'id': limit[0]}
                    )
                else:
                    dbwrapper.insert_value(dbwrapper.LIMIT_TABLE, {
                        'amount': update.message.text,
                        "container_id": user_data[UserDataKey.CONTAINER],
                        "product_id": user_data['data']
                    },)

        else:
            if int(update.message.text) == 0:
                dbwrapper.delete_value(dbwrapper.INSTANCE_TABLE, {'id': user_data['data']})
            else:
                dbwrapper.update_value(dbwrapper.INSTANCE_TABLE,
                    {
                        'amount': update.message.text,
                        "date": "'%s'" % datetime.now(),
                        "editor": "'%s'" % update.effective_user.name,
                    },
                    {'id': user_data['data']}
                )

        return await start(update, context)

    elif user_data[UserDataKey.ACTION] == Action.ADD:
        if int(update.message.text) != 0:
            dbwrapper.insert_value(dbwrapper.INSTANCE_TABLE, {
                "product_id": user_data[UserDataKey.PRODUCT],
                "location_id": user_data[UserDataKey.LOCATION],
                "container_id": user_data[UserDataKey.CONTAINER],
                "amount": update.message.text,
                "date": datetime.now(),
                "editor": update.effective_user.name,
            })
        await start(update, context)
        return State.CHOOSING_ACTION
    
    else:
        logging.error("Unexpected action: %s" % user_data[UserDataKey.ACTION])


    reset_data(context)

    return await start(update, context)

async def add_container(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=NEW_CONTAINER_SYMB_TEXT)

    return State.ENTERING_CONTAINER_SYMBOL

async def on_container_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    user_data = context.user_data

    if user_data[UserDataKey.ACTION] == Action.UPDATE:
        dbwrapper.update_value(dbwrapper.CONTAINER_TABLE,
            {
                'amount': update.message.text,
                "date": datetime.now(),
                "editor": update.effective_user.name,
            },
            {'id': user_data['data']}
        )
        return await start(update, context)

    elif user_data[UserDataKey.ACTION] == Action.ADD:
        user_data[UserDataKey.CONTAINER_SYMBOL] = update.message.text
        return await add_container_description(update, context)
    
    else:
        logging.error("Unexpected action: %s" % user_data[UserDataKey.ACTION])

async def add_container_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)
    user_data = context.user_data

    message = NEW_CONTAINER_DESC_TEXT % user_data[UserDataKey.CONTAINER_SYMBOL]

    if update.callback_query:
        await update.callback_query.edit_message_text(text=message)
    else:
        await update.message.reply_text(text=message)

    return State.ENTERING_CONTAINER_DESCRIPTION

async def on_container_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    logging.info(inspect.stack()[0][0].f_code.co_name)
    user_data = context.user_data

    dbwrapper.insert_value(dbwrapper.CONTAINER_TABLE, {
        "description": update.message.text,
        "symbol": user_data[UserDataKey.CONTAINER_SYMBOL]
    })

    return await start(update, context)


async def add_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=NEW_LOCATION_TEXT)

    return State.ENTERING_LOCATION

async def on_add_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(inspect.stack()[0][0].f_code.co_name)

    dbwrapper.insert_value(dbwrapper.LOCATION_TABLE, {"name": update.message.text})
    # update.get_bot().send_message(chat_id, text)
    return await start(update, context)


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=NEW_PRODUCT_TEXT)

    return State.ENTERING_PRODUCT

async def on_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dbwrapper.insert_value(dbwrapper.PRODUCT_TABLE, {"name": update.message.text})
    return await start(update, context)

async def filtered_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    query_data = update.callback_query.data
    for key in query_data:
        context.user_data[key] = query_data[key]

    def constraint(product, location, amount, container, date, editor):
        if query_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
            return product == query_data['data']
        if query_data[UserDataKey.FIELD_TYPE] ==  UserDataKey.LOCATION:
            return location == query_data['data']
        logging.warning("unexpected filter")
        return True

    buttons = build_data_buttons(constraint)
    extra_buttons = []
    if query_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
        limits = dbwrapper.get_table(dbwrapper.LIMIT_TABLE)
        limit = next((x for x in limits if x[1] == query_data['data']), None)
        limit_str = "ніколи"

        if limit:
            logging.info(limit)
            containers = dbwrapper.get_table(dbwrapper.CONTAINER_TABLE)
            container = next((x for x in containers if x[0] == limit[3]), None)
            logging.info(container)
            limit_str = "%s %s" % (limit[2], container[1])

        extra_buttons.append(
            InlineKeyboardButton(text=LIMIT_CAPTION % limit_str, callback_data={
                    UserDataKey.ACTION: Action.UPDATE,
                    UserDataKey.FIELD_TYPE: UserDataKey.LIMIT
                }),
        )
    
    extra_buttons.append(
        InlineKeyboardButton(text=ACTION_DESCRIPTIONS[Action.DONE], callback_data={
                UserDataKey.ACTION: ConversationHandler.END,
                UserDataKey.FIELD_TYPE: UserDataKey.CONTAINER
            }),
    )

    buttons.append(extra_buttons)

    keyboard = InlineKeyboardMarkup(buttons)

    message = ""
    if query_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
        products = dbwrapper.get_table(dbwrapper.PRODUCT_TABLE)
        product_str = next((x for x in products if x[0] == query_data['data']), None)[1]
        message = FILTERED_VIEW_TEXT % product_str
    if query_data[UserDataKey.FIELD_TYPE] ==  UserDataKey.LOCATION:
        locations = dbwrapper.get_table(dbwrapper.LOCATION_TABLE)
        location_str = next((x for x in locations if x[0] == query_data['data']), None)[1]
        message = FILTERED_VIEW_TEXT % location_str

    await update.callback_query.edit_message_text(text=message, reply_markup=keyboard)

    return State.FILTERED_VIEW

async def on_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    # await update.callback_query.answer()
    query_data = update.callback_query.data

    if query_data[UserDataKey.ACTION] == Action.FILTER:
        return await filtered_view(update, context)

    elif query_data[UserDataKey.ACTION] == Action.UPDATE:
        for key in query_data:
            context.user_data[key] = query_data[key]
        return await select_container(update, context)

    return await start(update, context)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.message.reply_text(COMEBACK_TEXT, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=COMEBACK_TEXT)

    return ConversationHandler.END

# getter

def get_handler():


    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        # exit state -> handler
        states={
            State.CHOOSING_ACTION: [
                CallbackQueryHandler(on_storage_action),
            ],
            State.CHOOSING_LOCATION: [
                CallbackQueryHandler(on_location),
            ],
            State.CHOOSING_PRODUCT: [
                CallbackQueryHandler(on_product),
            ],
            State.CHOOSING_CONTAINER: [
                CallbackQueryHandler(on_container),
            ],
            State.ENTERING_LOCATION: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_add_location )
            ],
            State.ENTERING_PRODUCT: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_add_product )
            ],
            State.ENTERING_CONTAINER_SYMBOL: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_container_symbol )
            ],
            State.ENTERING_CONTAINER_DESCRIPTION: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_container_description )
            ],
            State.ENTERING_AMOUNT: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_amount )
            ],
            State.FILTERED_VIEW: [ CallbackQueryHandler(on_filter) ],
        },
        fallbacks=[
            CommandHandler("stop", stop),
            CallbackQueryHandler(stop, pattern="^" + str(ConversationHandler.END) + "$")
        ],
        allow_reentry=True
    )

