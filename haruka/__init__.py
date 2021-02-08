import logging
import aiohttp
from pyrogram import Client
from plate import Plate
from configparser import ConfigParser


async def get_bot():
    global BotID, BotName, BotUsername
    self = await app.get_me()
    BotID = self.id
    BotName = self.first_name
    BotUsername = self.username


HELPABLE = {}  # TODO
FORMAT = "[%(levelname)s - %(asctime)s] -> %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%d/%m/%Y %T")
LOGGER = logging.getLogger("rich")
parser = ConfigParser()
parser.read("config.ini")
bot_config = parser["botconfig"]
OWNER_ID = bot_config.getint("OWNER_ID")
DB_URI = bot_config.get("DB_URI")
plate = Plate()
httpsession = aiohttp.ClientSession()
BotName = ""
BotUsername = ""
BotID = 0
# TODO: move this to the database for per-user translations.
tmp_lang = "en_US"
app = Client(":memory:", config_file="config.ini")
