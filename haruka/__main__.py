import logging
import asyncio
import threading
from haruka import LOCAL, set_bot
from pyrogram.session import Session
from pyrogram import __version__, idle
from haruka.database import init_database
from haruka.database.util import ensure_bot_in_db
from haruka.modules.antifloodwait import background_watcher


async def run_async():
    """
    Asynchronous entry point for HarukaPyro
    """

    try:
        LOCAL.LOGGER.info("Starting the Telegram client")
        await LOCAL.APP.start()
        LOCAL.LOGGER.debug("Telegram client started")
        LOCAL.LOGGER.info("Retrieving information about ourselves")
        await set_bot()
        LOCAL.LOGGER.debug(f"Retrieved self: ID is {LOCAL.bot_id}, username is @{LOCAL.bot_username}")
        LOCAL.LOGGER.info("Initializing database")
        LOCAL.database_pool = await init_database(*LOCAL.DB_POOL_SIZE)
        LOCAL.LOGGER.debug(f"Initialized database pool: min={LOCAL.DB_POOL_SIZE[0]} and max={LOCAL.DB_POOL_SIZE[1]}")
        LOCAL.LOGGER.debug("Ensuring that we're in the database")
        await ensure_bot_in_db()
        LOCAL.LOGGER.info("Starting antiflood background watcher")
        threading.Thread(target=background_watcher,
                         args=(LOCAL.PURGE_POLLING_RATE, LOCAL.INACTIVE_THRESHOLD),
                         daemon=True).start()
        LOCAL.LOGGER.debug("Initialization complete")
        LOCAL.LOGGER.info("HarukaPyro started, going idle")
        await idle()
    except BaseException as error:
        LOCAL.LOGGER.error(f"Exiting due to a {type(error).__name__}: {error}")
    finally:
        LOCAL.LOGGER.warning("HarukaPyro is shutting down")
        await LOCAL.HTTP_SESSION.close()
        await LOCAL.database_pool.close()


if __name__ == "__main__":
    LOCAL.LOGGER.info(
        f"""Starting HarukaPyro, powered by Pyrogram (v{__version__}). Copyright (C) 2021 Intellivoid Technologies
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions, check the LICENSE file for more information.
    Haruka Aya is a registered trademark owned by Haruka LLC and licensed to Intellivoid Technologies.
    All rights and trademarks belong to their respective owners."""
    )
    LOCAL.LOGGER.debug("Initializing HarukaPyro")
    # Sets pyrogram logging to warning because info is too verbose
    LOCAL.LOGGER.debug("Setting pyrogram logs to warning to avoid verbose output and disabling the session notice")
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    Session.notice_displayed = True
    LOCAL.LOGGER.debug("Starting asyncio event loop")
    asyncio.run(run_async())
