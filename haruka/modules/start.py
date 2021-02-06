from logging import disable
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from haruka import app, plate, tmp_lang
from haruka.helpers import custom_filters

@app.on_message(~filters.me & custom_filters.command('start', prefixes='/'), group=8)
async def start(client, message):
    if message.chat.type != "private":
        await message.reply_text(plate("start_group", tmp_lang))
        return
    else:
        buttons = [[InlineKeyboardButton(plate("help_button_support", tmp_lang), url="https://t.me/HarukaAyaGroup"),
                    InlineKeyboardButton(plate("help_button_help", tmp_lang), callback_data='help_back')]]
        await message.reply_text(plate("start_private", tmp_lang), reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)