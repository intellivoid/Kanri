import re
from kanri import HELPABLE, LOCAL  # pylint: disable-msg=E0611
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from kanri.helpers import custom_filters
from kanri.helpers.misc import paginate_modules


async def help_parser(client, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await client.send_message(chat_id, text, reply_markup=keyboard)


@Client.on_message(~filters.me & custom_filters.command('help', prefixes='/') & ~LOCAL.FLOOD_WAITED, group=8)
async def help_command(client, message):
    if message.chat.type != "private":
        username = (await client.get_me()).username
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=LOCAL.PLATE("help_button_help", LOCAL.DEFAULT_LANG),
                        url=f"t.me/{username}?start=help",
                    )
                ]
            ]
        )
        await message.reply(LOCAL.PLATE("help_group", LOCAL.DEFAULT_LANG), reply_markup=buttons)
    else:
        await help_parser(client, message.chat.id, LOCAL.PLATE("help_main", LOCAL.DEFAULT_LANG))


async def help_button_callback(_, __, query):
    if re.match(r"help_", query.data):
        return True


@Client.on_callback_query(filters.create(help_button_callback) & ~LOCAL.FLOOD_WAITED)
async def help_button(_client, query):
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    if mod_match:
        module = mod_match.group(1)
        text = LOCAL.PLATE("help_module", LOCAL.DEFAULT_LANG, name=HELPABLE[module].__mod_name__)
        text += LOCAL.PLATE(HELPABLE[module].__help__, LOCAL.DEFAULT_LANG)

        await query.message.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=LOCAL.PLATE("generic_back", LOCAL.DEFAULT_LANG),
                            callback_data="help_back",
                        )
                    ]
                ]
            ),
        )

    elif back_match:
        await query.message.edit(
            text=LOCAL.PLATE("help_main", LOCAL.DEFAULT_LANG),
            reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
        )
