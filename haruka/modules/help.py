import re
import time

from __main__ import HELPABLE # pylint: disable-msg=E0611
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.raw import functions

from haruka import app, BotUsername, plate, tmp_lang
from haruka.helpers import custom_filters
from haruka.helpers.misc import paginate_modules

async def help_parser(client, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(~filters.me & custom_filters.command('help', prefixes='/'), group=8)
async def help_command(client, message):
    if message.chat.type != "private":
        username = (await client.get_me()).username
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=plate("help_button_help", tmp_lang), url=f"t.me/{username}?start=help")]])
        await message.reply(plate("help_group", tmp_lang), reply_markup=buttons)
    else:
        await help_parser(client, message.chat.id, plate("help_main", tmp_lang))


async def help_button_callback(_, __, query):
    if re.match(r"help_", query.data):
        return True


@app.on_callback_query(filters.create(help_button_callback))
async def help_button(_client, query):
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    if mod_match:
        module = mod_match.group(1)
        text = plate("help_module", tmp_lang, name=HELPABLE[module].__mod_name__)
        text += plate(HELPABLE[module].__help__, tmp_lang)

        await query.message.edit(text=text,
                                reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(text=plate("generic_back", tmp_lang), callback_data="help_back")]]))

    elif back_match:
        await query.message.edit(text=plate("help_main", tmp_lang),
                    reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))