from kanri import LOCAL
from kanri.database import users as chats_db
from pyrogram import filters, Client
from kanri.helpers import custom_filters
from io import BytesIO


@Client.on_message(
    filters.user(LOCAL.OWNER_ID) & custom_filters.command("stats", prefixes='/') & ~LOCAL.FLOOD_WAITED
)
async def stats_text(_, message):
    stats = "──「 <b>Current stats</b> 」──\n"
    stats += f"-> `{chats_db.num_users()}` users, across `{chats_db.num_chats()}` chats"
    await message.reply(stats)


@Client.on_message(
    ~filters.me & filters.user(LOCAL.OWNER_ID) & custom_filters.command("chats", prefixes='/') & ~LOCAL.FLOOD_WAITED
)
async def chat_stats(client, message):
    all_chats = chats_db.get_all_chats() or []
    with BytesIO(b"") as output:
        output.write(b"List of chats.\n Chat name | Chat ID | Members count\n")
        for i, chat in enumerate(all_chats):
            chat_members = await client.get_chat_members_count(chat.chat_id)
            output.write(
                "{}. {} | {} | {}\n".format(
                    i + 1, chat.chat_name, chat.chat_id, chat_members
                ).encode()
            )
        output.name = "chats.txt"
        output.seek(0)
        await message.reply_document(
            document=output, caption="Here is the list of chats in my database."
        )


@Client.on_message(filters.all & filters.group & ~LOCAL.FLOOD_WAITED, group=-1)
async def log_user(_, message):
    chat = message.chat
    await chats_db.update_user(
        message.from_user.id, message.from_user.username, chat.id, chat.title
    )
    if message.reply_to_message:
        await chats_db.update_user(
            message.reply_to_message.from_user.id,
            message.reply_to_message.from_user.username,
            chat.id,
            chat.title,
        )
    if message.forward_from:
        await chats_db.update_user(message.forward_from.id, message.forward_from.username)
