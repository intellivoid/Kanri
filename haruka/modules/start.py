from logging import disable
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from haruka import app
from haruka.helpers import custom_filters

prvt_message = '''
Hey there! My name is Haruka Aya - I'm here to help you manage your groups!
Click Help button to find out more about how to use me to my full potential.
Join [the bot support group](https://t.me/HarukaAyaGroup) ( @HarukaAyaGroup ) if you need any bot support or help.
Follow [Haruka Aya](https://t.me/HarukaAya) ( @HarukaAya ) if you want to keep up with the bot news, bot updates and bot downtime!
Made with love by @RealAkito\n\nWant to add me to your group? [Click here!](t.me/HarukaAyaBot?startgroup=true)

'''

grp_message = '''
Hey there! I'm alive :3
'''

@app.on_message(~filters.me & custom_filters.command('start', prefixes='/'), group=8)
async def start(client, message):
    if message.chat.type != "private":
        await message.reply_text(grp_message)
        return
    else:
        buttons = [[InlineKeyboardButton("Support Chat", url="https://t.me/HarukaAyaGroup"),
                    InlineKeyboardButton('Help', callback_data='help_back')]]
        await message.reply_text(prvt_message, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)