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

from telegram.ext import Application

# shut up, warning!

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
filterwarnings(action="ignore", message=r".*CallbackQueryHandler",category=PTBUserWarning)

TG_TOKEN = os.environ["TG_TOKEN"]
PORT = int(os.environ.get('PORT', '8443'))

# Enable logging
logging.basicConfig(
    # format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(TG_TOKEN).arbitrary_callback_data(True).build()

    application.add_handler(callbacks.get_handler())

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
