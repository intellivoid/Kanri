import logging
import threading
import aiohttp
from pyrogram import Client, filters
from plate import Plate
from configparser import ConfigParser


HELPABLE = {}  # TODO
parser = ConfigParser()
parser.read("config.ini")
bot_config = parser["bot"]
database_config = parser["database"]
logging_config = parser["logging"]
lang_config = parser["lang"]
anti_flood_wait_config = parser["anti_flood_wait"]

# We use thread-local space to minimize the
# amount of globals that we import to just 1
LOCAL = threading.local()
# Runtime "constants", do not touch these!
# Use the config.ini file instead
LOCAL.ANTIFLOOD_SENSIBILITY = anti_flood_wait_config.getint("sensibility")
LOCAL.MAX_UPDATE_THRESHOLD = anti_flood_wait_config.getint("max_update_threshold")
LOCAL.FLOOD_PERCENTAGE = anti_flood_wait_config.getint("flood_percentage")
LOCAL.BAN_TIME = anti_flood_wait_config.getint("ban_time")
LOCAL.DELETE_MESSAGES = anti_flood_wait_config.getboolean("delete_messages")
LOCAL.FLOOD_NOTICE = anti_flood_wait_config.get("flood_notice")
LOCAL.PURGE_POLLING_RATE = anti_flood_wait_config.getint("purge_polling_rate")
LOCAL.INACTIVE_THRESHOLD = anti_flood_wait_config.getint("inactive_threshold")
LOCAL.FLOOD_WAITED = filters.user()
LOCAL.OWNER_ID = bot_config.getint("owner_id")
LOCAL.DB_URI = database_config.get("db_uri")
LOCAL.DB_POOL_SIZE = (database_config.getint("min_pool_size"), database_config.getint("max_pool_size"))
logging.basicConfig(
                    format=logging_config.get("format"),
                    datefmt=logging_config.get("date_format"))
LOCAL.LOGGER = logging.getLogger("harukapyro")
LOCAL.LOGGER.setLevel(logging_config.getint("level"))
LOCAL.PLATE = Plate()
LOCAL.HTTP_SESSION = aiohttp.ClientSession()
# TODO: move this to the database for per-user translations.
LOCAL.DEFAULT_LANG = lang_config.get("default")
LOCAL.APP = Client(":memory:", config_file="config.ini")


async def set_bot():
    """
    Sets the bot's own username and ID
    in the thread-local storage space
    """

    self = await LOCAL.APP.get_me()
    LOCAL.bot_id = self.id
    LOCAL.bot_name = self.first_name
    LOCAL.bot_username = self.username
