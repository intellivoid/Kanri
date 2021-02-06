import re
import time

from __main__ import HELPABLE # pylint: disable-msg=E0611
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.raw import functions

from haruka import app, BotUsername
from haruka.helpers import custom_filters
from haruka.helpers.misc import paginate_modules


HELP_STRINGS = f"""
Hey! My name is **Haruka**. I am a group management bot, here to help you get around and keep the order in your groups!
I have lots of handy features, such as warning system, a note keeping system, and even predetermined replies on certain keywords.\n
**Helpful commands:**
- /start: Starts me! You've probably already used this.
- /help: Sends this message; I'll tell you more about myself!
"""

async def help_parser(client, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(~filters.me & custom_filters.command('help', prefixes='/'), group=8)
async def help_command(client, message):
    if message.chat.type != "private":
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Help",
                url=f"t.me/{BotUsername}?start=help")]])
        await message.reply("Contact me in PM to get the list of possible commands.",
                            reply_markup=buttons)
    else:
        await help_parser(client, message.chat.id, HELP_STRINGS)


async def help_button_callback(_, __, query):
    if re.match(r"help_", query.data):
        return True


@app.on_callback_query(filters.create(help_button_callback))
async def help_button(_client, query):
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    if mod_match:
        module = mod_match.group(1)
        text = "This is help for the module **{}**:\n".format(HELPABLE[module].__mod_name__) \
            + HELPABLE[module].__help__

        await query.message.edit(text=text,
                                reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

    elif back_match:
        await query.message.edit(text=HELP_STRINGS,
                    reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))