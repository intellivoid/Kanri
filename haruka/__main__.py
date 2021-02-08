import logging
import aiohttp
import asyncio
from pyrogram import Client, __version__, idle
from pyrogram.session import Session
from haruka import httpsession, get_bot, app, LOGGER, FORMAT


async def run_async(client: Client, session: aiohttp.ClientSession):
    """
    Asynchronous entry point for HarukaPyro
    """

    try:
        await client.start()
        LOGGER.info("HarukaPyro started")
        await get_bot()
        await idle()
    except BaseException as error:
        LOGGER.error(f"Exiting due to a {type(error).__name__}: {error}")
    finally:
        await session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%d/%m/%Y %T")
    LOGGER.info(
        f"""Starting HarukaPyro, powered by Pyrogram (v{__version__}). Copyright (C) 2021 Intellivoid Technologies
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions, check the LICENSE file for more information.
    Haruka Aya is a registered trademark owned by Haruka LLC and licensed to Intellivoid Technologies.
    All rights and trademarks belong to their respective owners."""
    )
    # Sets pyrogram logging to warning because info is too verbose
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    Session.notice_displayed = True
    try:
        asyncio.run(run_async(app, httpsession))
    except AttributeError:
        # Python < 3.6
        asyncio.get_event_loop().run_until_complete(run_async(app, httpsession))
