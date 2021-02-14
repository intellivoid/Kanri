from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from kanri import LOCAL
from kanri.helpers import custom_filters

# Start buttons
BUTTONS = [
    [
        InlineKeyboardButton(
            LOCAL.PLATE("help_button_support", LOCAL.DEFAULT_LANG),
            url="https://t.me/KanriGroup",
        ),
        InlineKeyboardButton(
            LOCAL.PLATE("help_button_help", LOCAL.DEFAULT_LANG), callback_data='help_back'
        ),
    ]
]


@Client.on_message(~filters.me & custom_filters.command('start', prefixes='/') & ~LOCAL.FLOOD_WAITED, group=8)
async def start(_, message):
    if message.chat.type != "private":
        await message.reply_text(LOCAL.PLATE("start_group", LOCAL.DEFAULT_LANG))
    else:
        await message.reply_text(
            LOCAL.PLATE("start_private", LOCAL.DEFAULT_LANG),
            reply_markup=InlineKeyboardMarkup(BUTTONS),
            disable_web_page_preview=True,
        )
