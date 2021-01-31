from haruka import app, OWNER_ID, BotID
from haruka.modules.sql import users_sql as chats_db
from pyrogram import filters
from io import StringIO, BytesIO


@app.on_message(filters.user(OWNER_ID) & filters.command("stats", prefixes='/'))
async def stats_text(_, message):
    stats = "──「 <b>Current stats</b> 」──\n"
    stats += f"-> <code>{chats_db.num_users()}</code> users, across <code>{chats_db.num_chats()}</code> chats"
    await message.reply(stats)


@app.on_message(~filters.me & filters.user(OWNER_ID) & filters.command("chats", prefixes='/'))
async def chat_stats(client, message):
    all_chats = chats_db.get_all_chats() or []
    chatfile = 'List of chats.\n0. Chat name | Chat ID | Members count\n'
    P = 1
    for chat in all_chats:
        curr_chat = await client.get_chat(chat.chat_id)
        bot_member = await curr_chat.get_member(BotID)
        chat_members = await client.get_chat_members_count(chat.chat_id)
        chatfile += "{}. {} | {} | {}\n".format(P, chat.chat_name,
                                                    chat.chat_id, chat_members)
        P += 1

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "chatlist.txt"
        await message.reply_document(
            document=output,
            caption="Here is the list of chats in my database.")



@app.on_message(filters.all & filters.group)
def log_user(client, message):
    chat = message.chat
    chats_db.update_user(message.from_user.id, message.from_user.username, chat.id,
                    chat.title)

    if message.reply_to_message:
        chats_db.update_user(message.reply_to_message.from_user.id,
                        message.reply_to_message.from_user.username, chat.id,
                        chat.title)

    if message.forward_from:
        chats_db.update_user(message.forward_from.id, message.forward_from.username)