from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from haruka import plate, tmp_lang, app
from haruka.helpers import custom_filters

# Start buttons
BUTTONS = [
    [
        InlineKeyboardButton(
            plate("help_button_support", tmp_lang),
            url="https://t.me/HarukaAyaGroup",
        ),
        InlineKeyboardButton(
            plate("help_button_help", tmp_lang), callback_data='help_back'
        ),
    ]
]


@Client.on_message(~filters.me & custom_filters.command('start', prefixes='/'), group=8)
async def start(_, message):
    if message.chat.type != "private":
        await message.reply_text(plate("start_group", tmp_lang))
    else:
        await message.reply_text(
            plate("start_private", tmp_lang),
            reply_markup=InlineKeyboardMarkup(BUTTONS),
            disable_web_page_preview=True,
        )
