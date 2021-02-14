from datetime import datetime
from pyrogram import filters, Client
from pyrogram.types import User, Message
from pyrogram.errors import PeerIdInvalid
from kanri import LOCAL
from kanri.helpers import custom_filters

__mod_name__ = "Info"
__help__ = "info_help"


def reply_check(message: Message):
    reply_id = None
    if message.reply_to_message:
        reply_id = message.reply_to_message.message_id
    elif not message.from_user.is_self:
        reply_id = message.message_id
    return reply_id


def last_online(user: User):
    if user.is_bot:
        return LOCAL.PLATE("info_status_online", LOCAL.DEFAULT_LANG)  # bots are always online
    elif user.status == 'recently':
        return LOCAL.PLATE("info_status_recently", LOCAL.DEFAULT_LANG)
    elif user.status == 'within_week':
        return LOCAL.PLATE("info_status_within_week", LOCAL.DEFAULT_LANG)
    elif user.status == 'within_month':
        return LOCAL.PLATE("info_status_within_month", LOCAL.DEFAULT_LANG)
    elif user.status == 'long_time_ago':
        return LOCAL.PLATE("info_status_long_time_ago", LOCAL.DEFAULT_LANG)
    elif user.status == 'online':
        return LOCAL.PLATE("info_status_online", LOCAL.DEFAULT_LANG)
    elif user.status == 'offline':
        return datetime.fromtimestamp(user.status.date).strftime(
            "%a, %d %b %Y, %H:%M:%S"
        )


@Client.on_message(~filters.me & custom_filters.command('info') & ~LOCAL.FLOOD_WAITED)
async def whois(client, message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await client.get_users(get_user)
    except PeerIdInvalid:
        await message.reply(LOCAL.PLATE("generic_unknown_user", LOCAL.DEFAULT_LANG))
        return
    desc = await client.get_chat(get_user)
    desc = desc.description
    info_text = LOCAL.PLATE(
        "info_infotext",
        LOCAL.DEFAULT_LANG,
        user_id=user.id,
        first_name=user.first_name if user.first_name else "",
        last_name=user.last_name if user.last_name else "",
        username=user.username if user.username else "",
        last_online=last_online(user),
        seen_chats=0,
        bio=desc if desc else LOCAL.PLATE("info_no_bio", LOCAL.DEFAULT_LANG),
    )
    await message.reply_text(info_text, disable_web_page_preview=True)
