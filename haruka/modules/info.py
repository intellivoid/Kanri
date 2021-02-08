from datetime import datetime
from pyrogram import filters, Client
from pyrogram.types import User, Message
from pyrogram.errors import PeerIdInvalid
from haruka import plate, tmp_lang
from haruka.helpers import custom_filters

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
        return plate("info_status_online", tmp_lang)  # bots are always online
    elif user.status == 'recently':
        return plate("info_status_recently", tmp_lang)
    elif user.status == 'within_week':
        return plate("info_status_within_week", tmp_lang)
    elif user.status == 'within_month':
        return plate("info_status_within_month", tmp_lang)
    elif user.status == 'long_time_ago':
        return plate("info_status_long_time_ago", tmp_lang)
    elif user.status == 'online':
        return plate("info_status_online", tmp_lang)
    elif user.status == 'offline':
        return datetime.fromtimestamp(user.status.date).strftime(
            "%a, %d %b %Y, %H:%M:%S"
        )


@Client.on_message(~filters.me & custom_filters.command('info'))
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
        await message.reply(plate("generic_unknown_user", tmp_lang))
        return

    desc = await client.get_chat(get_user)
    desc = desc.description
    info_text = plate(
        "info_infotext",
        tmp_lang,
        user_id=user.id,
        first_name=user.first_name if user.first_name else "",
        last_name=user.last_name if user.last_name else "",
        username=user.username if user.username else "",
        last_online=last_online(user),
        seen_chats=0,
        bio=desc if desc else plate("info_no_bio", tmp_lang),
    )

    await message.reply_text(info_text, disable_web_page_preview=True)
