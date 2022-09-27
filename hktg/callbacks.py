
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

class Action(Enum):
    SHOW = 1
    ADD = 2
    REMOVE = 3
    UPDATE = 4
    BACK = 5
    DONE = ConversationHandler.END

# userdata keys for values
class UserDataKey(Enum):
    ACTION = 1
    PRODUCT = 2
    LOCATION = 3
    AMOUNT = 4
    NEW_TEXT = 5
    FIELD_TYPE = 6

ACTION_DESCRIPTIONS = {
    Action.SHOW: "🔍 Показати",
    Action.ADD: "➕ Додати",
    Action.REMOVE: "Видалити",
    Action.UPDATE: "Оновити",
    Action.BACK: "Назад",
    Action.DONE: "Закінчити",
}

WELCOME_TEXT = "Ви можете обновити інформацію щодо складу. Щоб зупинити, просто введіть команду /stop."
COMEBACK_TEXT = "Повертайся скоріш! Для цього використай /start"
PROCESSED_TEXT = "Neat! Just so you know, this is what you already told me:"
NEW_LOCATION_TEXT = "І як нове місце називається?"
NEW_PRODUCT_TEXT = "І як новий продукт називається?"
AMOUNT_MESSAGE = "І скільки ж стало '%s' в '%s'?"
ADD_AMOUNT_MESSAGE = "I скільки ж '%s' зʼявилось в '%s'"
SHOWING_TEXT = "🔍 Ось що в нас є:"

REMOVE_CAPTION = "❌"

# common


def clear_field(key, context):

    if key in context.user_data:
        del context.user_data[key]


def reset_data(context: ContextTypes.DEFAULT_TYPE):

    for key in UserDataKey:
        clear_field(key, context)

# def get_data_buttons():


# ask for action
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    instances = dbwrapper.get_instance_list()
    locations = dbwrapper.get_location_list()
    products =  dbwrapper.get_product_list()

    buttons = []
    for ( id, product, location, amount, date, editor ) in instances:
        location_str = next((x for x in locations if x[0] == location), None)[1]
        product_str = next((x for x in products if x[0] == product), None)[1]
        buttons.append([
            InlineKeyboardButton(text=str(amount), callback_data={
                UserDataKey.ACTION: Action.UPDATE,
                UserDataKey.FIELD_TYPE: UserDataKey.AMOUNT,
                'data': id
            } ),
            InlineKeyboardButton(text=str(product_str), callback_data={
                UserDataKey.ACTION: Action.UPDATE,
                UserDataKey.FIELD_TYPE: UserDataKey.PRODUCT,
                'data': id
            }),
            InlineKeyboardButton(text=str(location_str), callback_data={
                UserDataKey.ACTION: Action.UPDATE,
                UserDataKey.FIELD_TYPE: UserDataKey.LOCATION,
                'data': id
            }),
            InlineKeyboardButton(text=REMOVE_CAPTION, callback_data={
                UserDataKey.ACTION: Action.REMOVE,
                'data': id
            }),
        ])
    buttons.append([
        InlineKeyboardButton(text=ACTION_DESCRIPTIONS[Action.ADD], callback_data={
                UserDataKey.ACTION: Action.ADD,
                UserDataKey.FIELD_TYPE: UserDataKey.AMOUNT
            }),
        InlineKeyboardButton(text=ACTION_DESCRIPTIONS[Action.DONE], callback_data={
                UserDataKey.ACTION: ConversationHandler.END,
                UserDataKey.FIELD_TYPE: UserDataKey.AMOUNT
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
    user_data = update.callback_query.data
    for key in user_data:
        context.user_data[key] = user_data[key]

    if user_data[UserDataKey.ACTION] == ConversationHandler.END:
        return await end(update, context)

    elif user_data[UserDataKey.ACTION] == Action.ADD:

        await select_location(update, context)
        return State.CHOOSING_LOCATION

    elif user_data[UserDataKey.ACTION] == Action.SHOW:

        await select_location(update, context)
        return State.CHOOSING_LOCATION

    elif user_data[UserDataKey.ACTION] == Action.UPDATE:

        if user_data[UserDataKey.FIELD_TYPE] == UserDataKey.AMOUNT:
            await ask_amount(update, context)
            return State.ENTERING_AMOUNT
        elif user_data[UserDataKey.FIELD_TYPE] == UserDataKey.PRODUCT:
            await select_product(update, context)
            return State.CHOOSING_PRODUCT
        elif user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LOCATION:
            await select_location(update, context)
            return State.CHOOSING_LOCATION


async def select_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    locations = dbwrapper.get_location_list()
    buttons = []
    for location_id, location_name in locations:
        buttons.append([InlineKeyboardButton(text=location_name, callback_data=location_id),])

    buttons.append([InlineKeyboardButton(text=ACTION_DESCRIPTIONS[ Action.ADD ], callback_data={
        "action": Action.ADD
    })])

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

    products = dbwrapper.get_product_list()
    buttons = []
    for product_id, product_name, product_limit in products:
        buttons.append([InlineKeyboardButton(text=product_name, callback_data=product_id),])

    buttons.append([InlineKeyboardButton(text=ACTION_DESCRIPTIONS[ Action.ADD ], callback_data={
        "action": Action.ADD
    })])
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text="Виберіть продукцію:", reply_markup=keyboard)

    return State.CHOOSING_PRODUCT


async def on_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    selected_product =  update.callback_query.data

    if isinstance(selected_product, dict):
        return await add_product(update, context)

    if context.user_data[UserDataKey.ACTION] == Action.UPDATE:
        if context.user_data[UserDataKey.FIELD_TYPE] == UserDataKey.LOCATION:
            dbwrapper.update_value(dbwrapper.INSTANCE_TABLE, {'product_id': selected_product}, {'id': context.user_data['data']})
            return await start(update, context)
    elif context.user_data[UserDataKey.ACTION] == Action.ADD:
        context.user_data[UserDataKey.PRODUCT] = selected_product
        return await ask_amount(update, context)


async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    # clear_field( UserDataKey.NEW_TEXT, context )

    user_data = context.user_data
    message = ""

    instances = dbwrapper.get_instance_list()
    products = dbwrapper.get_product_list()
    locations = dbwrapper.get_location_list()

    if user_data[UserDataKey.ACTION] == Action.UPDATE:

        instance = next((x for x in instances if x[0] == user_data['data']), None)
        ( id, product_id, location_id, amount, date, editor ) = instance
        product_name = next((x for x in products if x[0] == product_id), None)[1]
        location_name = next((x for x in locations if x[0] == location_id), None)[1]
        message = AMOUNT_MESSAGE % (product_name, location_name)
    
    elif user_data[UserDataKey.ACTION] == Action.ADD:

        product_name = next((x for x in products if x[0] == user_data[UserDataKey.PRODUCT]), None)[1]
        location_name = next((x for x in locations if x[0] ==  user_data[UserDataKey.LOCATION]), None)[1]
        message = ADD_AMOUNT_MESSAGE % (product_name, location_name)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=message)

    return State.ENTERING_AMOUNT


async def on_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    user_data = context.user_data

    if user_data[UserDataKey.ACTION] == Action.UPDATE:
        dbwrapper.update_value(dbwrapper.INSTANCE_TABLE, 
            {
                'amount': update.message.text,
                "date": datetime.now(),
                "editor": update.effective_user.name,
            },
            {'id': user_data['data']}
        )
        await start(update, context)
        return State.CHOOSING_ACTION

    elif user_data[UserDataKey.ACTION] == Action.ADD:
        dbwrapper.insert_value(dbwrapper.INSTANCE_TABLE, {
            "product_id": user_data[UserDataKey.PRODUCT],
            "location_id": user_data[UserDataKey.LOCATION],
            "amount": update.message.text,
            "date": datetime.now(),
            "editor": update.effective_user.name,
        })
        await start(update, context)
        return State.CHOOSING_ACTION
    
    else:
        logging.error("Unexpected action: %s" % user_data[UserDataKey.ACTION])

    # if context.user_data[UserDataKey.CURRENT_TEXT_TYPE] == UserDataKey.AMOUNT:
    #    current_tier[ UserDataKey.AMOUNT ](
    #         user_data[UserDataKey.LOCATION],
    #         user_data[UserDataKey.PRODUCT],
    #         entered_text
    #     )
    # elif UserDataKey.PRODUCT in user_data:
    #    current_tier[ UserDataKey.PRODUCT ](
    #         user_data[UserDataKey.PRODUCT],
    #         entered_text
    #     )
    # elif UserDataKey.LOCATION in user_data:
    #    current_tier[ UserDataKey.LOCATION ](
    #         user_data[UserDataKey.LOCATION],
    #         entered_text
    #     )


    reset_data(context)

    return await start(update, context)

async def add_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=NEW_LOCATION_TEXT)

    return State.ENTERING_LOCATION

async def on_add_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dbwrapper.insert_value(dbwrapper.LOCATION_TABLE, {"name": update.message.text})
    return await start(update, context)

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    logging.info(inspect.stack()[0][0].f_code.co_name)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=NEW_PRODUCT_TEXT)

    return State.ENTERING_PRODUCT

async def on_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dbwrapper.insert_value(dbwrapper.PRODUCT_TABLE, {"name": update.message.text})
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
            State.ENTERING_AMOUNT: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_amount )
            ],
            State.ENTERING_LOCATION: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_add_location )
            ],
            State.ENTERING_PRODUCT: [
                MessageHandler( filters.TEXT & ~filters.COMMAND, on_add_product )
            ],
        },
        fallbacks=[
            CommandHandler("stop", stop),
            CallbackQueryHandler(stop, pattern="^" + str(ConversationHandler.END) + "$")
        ],
        allow_reentry=True
    )

