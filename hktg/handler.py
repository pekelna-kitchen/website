
# from typing import Any, Dict, Tuple
# import logging
# from datetime import datetime

from telegram import (
    # ReplyKeyboardMarkup,
    # ReplyKeyboardRemove,
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

from hktg import dbwrapper, callbacks
from hktg.constants import *

def get():

    return ConversationHandler(
        entry_points=[CommandHandler("start", callbacks.Home.ask)],

        states={
            State.CHOOSING_ACTION: [CallbackQueryHandler(callbacks.Home.answer)],
            # State.CHOOSING_LOCATION: [CallbackQueryHandler(select_location.SelectLocation.answer)],
            State.CHOOSING_PRODUCT: [CallbackQueryHandler(callbacks.SelectProduct.answer)],
            State.CHOOSING_CONTAINER: [CallbackQueryHandler(callbacks.SelectContainer.answer)],
            State.ENTERING_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.AddLocation.answer)],
            State.ENTERING_PRODUCT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.AddProduct.answer)
            ],
            State.ENTERING_CONTAINER_SYMBOL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.AddContainerSymbol.answer)
            ],
            State.ENTERING_CONTAINER_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.AddContainerDescription.answer)
            ],
            State.ENTERING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.AskAmount.answer)
            ],
            State.FILTERED_VIEW: [CallbackQueryHandler(callbacks.FilteredView.answer)],
            State.VIEWING_ENTRY: [CallbackQueryHandler(callbacks.ViewEntry.answer)],
        },
        fallbacks=[
            CommandHandler("stop", callbacks.Home.stop),
            CallbackQueryHandler(callbacks.Home.stop)
        ],
        allow_reentry=True
    )
