import time
import logging
from haruka import LOCAL
from itertools import tee
from pyrogram import Client
from pyrogram.types import Message
from collections import defaultdict
from pyrogram.errors import RPCError


# Stores messages to be checked for flood later
MESSAGES = defaultdict(list)
# Stores users' ban expirations
BANNED = {}


def is_flood(updates: list):
    """
    Calculates if a sequence of
    updates corresponds to a flood
    """

    # TODO: This is hacky and partially stolen from stackoverflow
    #  Make it work properly with odd update thresholds!
    # Credits to @kuogi on Telegram for sharing the antiflood
    # logic and god bless stackoverflow for the pairwise
    # iteration snippet
    a, b = tee(updates)
    next(b, None)
    # We invert the subtraction (y - x instead of x - y) to avoid
    # getting a negative result which would always be below threshold
    # (we could use abs() but whatever)
    return sum((y - x) <= LOCAL.ANTIFLOOD_SENSIBILITY for x, y in zip(a, b)) >= int((len(updates) / 100) * LOCAL.FLOOD_PERCENTAGE)


@Client.on_message(group=-1000)
async def anti_flood(client: Client, update: Message):
    """
    Anti flood handler
    """

    if not update.from_user:
        # If this doesn't come from a user
        # we can't do much and we won't process
        # it anyway
        return
    try:
        user_id = update.from_user.id
        chat = update.chat.id
        date = time.time()
        message_id = update.message_id
        if user_id in BANNED:
            chat, date = BANNED[user_id]
            if time.time() - date >= LOCAL.BAN_TIME:
                LOCAL.LOGGER.debug(f"{user_id} has waited at least {LOCAL.BAN_TIME} seconds in {chat} and can now text again")
                LOCAL.FLOOD_WAITED.remove(user_id)
                MESSAGES[(user_id, chat)] = [(date, message_id)]
                BANNED.pop(user_id)
        elif len(MESSAGES[(user_id, chat)]) >= LOCAL.MAX_UPDATE_THRESHOLD - 1:  # -1 to avoid acting on the next update
            MESSAGES[(user_id, chat)].append((date, message_id))
            LOCAL.LOGGER.debug(f"MAX_UPDATE_THRESHOLD ({LOCAL.MAX_UPDATE_THRESHOLD}) Reached for {user_id}")
            user_data = MESSAGES.pop((user_id, chat))
            timestamps = [d[0] for d in user_data]
            updates = [d[1] for d in user_data]
            if is_flood(timestamps):
                LOCAL.LOGGER.warning(f"Flood detected from {user_id} in chat {chat}")
                LOCAL.FLOOD_WAITED.add(user_id)
                BANNED[user_id] = (user_id, time.time())
                if LOCAL.FLOOD_NOTICE:
                    await client.send_message(user_id, LOCAL.FLOOD_NOTICE, reply_to_message_id=update.message_id)
                if LOCAL.DELETE_MESSAGES:
                    await client.delete_messages(chat, updates)
        else:
            MESSAGES[(user_id, chat)].append((date, message_id))
    except RPCError as rpc_error:
        LOCAL.LOGGER.error(f"An RPC error occurred -> {rpc_error}")


def background_watcher(purge_polling_rate: int, inactive_threshold: int):
    """
    Watches in the background to make sure we don't keep
    around user entries inside RAM for too long if they
    haven't texted in a while
    """

    # We don't use LOCAL.LOGGER here because this is a separate thread
    logging.info("Background antiflood watcher started")
    while True:
        try:
            logging.info("Purging antiflood")
            purged = 0
            for (user, chat), data in MESSAGES.copy().items():
                if time.time() - data[-1][-1] >= inactive_threshold:   # The last message!
                    logging.debug(f"User {user} at {chat} has been inactive for more than {inactive_threshold} seconds")
                    del MESSAGES[user, chat]
                    purged += 1
            logging.info(f"Purged {purged} entries")
            time.sleep(purge_polling_rate)
        except Exception as err:
            logging.error(f"Background antiflood watcher exiting due to {type(err).__name__}: {err}")
            break


