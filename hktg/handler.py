
# from typing import Any, Dict, Tuple
# import logging
# from datetime import datetime

from telegram import (
    # ReplyKeyboardMarkup,
    # ReplyKeyboardRemove,
    # InlineKeyboardButton,
    # InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    ConversationHandler,
    # ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from hktg import dbwrapper
from hktg.callbacks import (
    home,
    filtered_view,
    view_entry,
    select_container,
    select_product,
    add_location,
    add_product,
    add_container_symbol,
    add_container_description,
    ask_amount
)
from hktg.constants import *

def get():

    return ConversationHandler(
        entry_points=[CommandHandler("start", home.Home.ask)],

        states={
            State.CHOOSING_ACTION: [CallbackQueryHandler(home.Home.answer)],
            # State.CHOOSING_LOCATION: [CallbackQueryHandler(select_location.SelectLocation.answer)],
            State.CHOOSING_PRODUCT: [CallbackQueryHandler(select_product.SelectProduct.answer)],
            State.CHOOSING_CONTAINER: [CallbackQueryHandler(select_container.SelectContainer.answer)],
            State.ENTERING_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location.AddLocation.answer)],
            State.ENTERING_PRODUCT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_product.AddProduct.answer)
            ],
            State.ENTERING_CONTAINER_SYMBOL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_container_symbol.AddContainerSymbol.answer)
            ],
            State.ENTERING_CONTAINER_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_container_description.AddContainerDescription.answer)
            ],
            State.ENTERING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount.AskAmount.answer)
            ],
            State.FILTERED_VIEW: [CallbackQueryHandler(filtered_view.FilteredView.answer)],
            State.VIEWING_ENTRY: [CallbackQueryHandler(view_entry.ViewEntry.answer)],
        },
        fallbacks=[
            CommandHandler("stop", home.Home.stop),
            CallbackQueryHandler(home.Home.stop)
        ],
        allow_reentry=True
    )
