#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import logging
import os
from hktg import callbacks

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

# shut up, warning!

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

TG_TOKEN = os.environ["TG_TOKEN"]
PORT = int(os.environ.get('PORT', '8443'))

# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    application = Application.builder().token(TG_TOKEN).build()

    # Set up third level ConversationHandler (collecting features)
    # description_conv = ConversationHandler(
    #     entry_points=[
    #         CallbackQueryHandler(
    #             callbacks.select_feature, pattern="^" + str(callbacks.MALE) + "$|^" + str(callbacks.FEMALE) + "$"
    #         )
    #     ],
    #     states={
    #         callbacks.SELECTING_FEATURE: [
    #             CallbackQueryHandler(callbacks.ask_for_input, pattern="^(?!" + str(END) + ").*$")
    #         ],
    #         callbacks.TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, callbacks.save_input)],
    #     },
    #     fallbacks=[
    #         CallbackQueryHandler(callbacks.end_describing, pattern="^" + str(END) + "$"),
    #         CommandHandler("stop", callbacks.stop_nested),
    #     ],
    #     map_to_parent={
    #         # Return to second level menu
    #         END: callbacks.SELECTING_LEVEL,
    #         # End conversation altogether
    #         callbacks.STOPPING: callbacks.STOPPING,
    #     },
    # )

    # # Set up second level ConversationHandler (adding a person)
    # add_member_conv = ConversationHandler(
    #     entry_points=[CallbackQueryHandler(callbacks.select_level, pattern="^" + str(callbacks.ADDING_MEMBER) + "$")],
    #     states={
    #         callbacks.SELECTING_LEVEL: [
    #             CallbackQueryHandler(callbacks.select_gender, pattern=f"^{callbacks.PARENTS}$|^{callbacks.CHILDREN}$")
    #         ],
    #         callbacks.SELECTING_GENDER: [description_conv],
    #     },
    #     fallbacks=[
    #         CallbackQueryHandler(callbacks.show_data, pattern="^" + str(SHOWING) + "$"),
    #         CallbackQueryHandler(callbacks.end_second_level, pattern="^" + str(END) + "$"),
    #         CommandHandler("stop", callbacks.stop_nested),
    #     ],
    #     map_to_parent={
    #         # After showing data return to top level menu
    #         SHOWING: SHOWING,
    #         # Return to top level menu
    #         END: SELECTING_ACTION,
    #         # End conversation altogether
    #         STOPPING: END,
    #     },
    # )

    # Set up top level ConversationHandler (selecting action)
    # Because the states of the third level conversation map to the ones of the second level
    # conversation, we need to make sure the top level conversation can also handle them
    selection_handlers = [
        # add_member_conv,
        # CallbackQueryHandler(callbacks.show_data, pattern="^" + str(SHOWING) + "$"),
        # CallbackQueryHandler(callbacks.adding_self, pattern="^" + str(ADDING_SELF) + "$"),
        CallbackQueryHandler(callbacks.end, pattern="^" + str(END) + "$"),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", callbacks.start)],
        states={
            callbacks.SHOWING: [CallbackQueryHandler(callbacks.start, pattern="^" + str(END) + "$")],
            callbacks.SELECTING_ACTION: selection_handlers,
            # callbacks.SELECTING_LEVEL: selection_handlers,
            # callbacks.DESCRIBING_SELF: [description_conv],
            callbacks.STOPPING: [CommandHandler("start", callbacks.start)],
        },
        fallbacks=[CommandHandler("stop", callbacks.stop)],
    )

    application.add_handler(conv_handler)
    application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=TG_TOKEN,
        webhook_url='https://hk-warehouse.herokuapp.com/' + TG_TOKEN
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()