from pyrogram import Client
from configparser import ConfigParser
import logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
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


app = Client("memory", config_file="config.ini")

BotName = ""
BotUsername = ""
BotID = 0

async def get_bot():
    global BotID, BotName, BotUsername
    getbot = await app.get_me()
    BotID = getbot.id
    BotName = getbot.first_name
    BotUsername = getbot.username