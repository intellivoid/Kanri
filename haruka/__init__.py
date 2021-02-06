from pyrogram import Client
from plate import Plate
from configparser import ConfigParser
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)

LOGGER = logging.getLogger("rich")
LOGGER.info("owo starting haruka...")

parser = ConfigParser()
parser.read("config.ini")
botconfig = parser["botconfig"]

OWNER_ID = botconfig.getint("OWNER_ID")
DB_URI = botconfig.get("DB_URI")
LOAD = botconfig.get("LOAD").split()
LOAD = list(map(str, LOAD))
NOLOAD = botconfig.get("NOLOAD").split()
NOLOAD = list(map(str, NOLOAD))

plate = Plate()
app = Client(":memory:", config_file="config.ini")

BotName = ""
BotUsername = ""
BotID = 0

# TODO: move this to the database for per-user translations.
tmp_lang = "de_DE"

async def get_bot():
    global BotID, BotName, BotUsername
    getbot = await app.get_me()
    BotID = getbot.id
    BotName = getbot.first_name
    BotUsername = getbot.username