from typing import Union
from asyncpg.exceptions import PostgresError
from haruka.database import run_query, ChatMember
from haruka.database.chats import get_chat


async def insert_chat_member(chat_id: int, user_id: int):
    """
    Inserts a chat member in the database. Returns True on success and False
    upon failure

    :param chat_id: The chat's ID
    :type chat_id: int
    :param user_id: The member's ID
    :type user_id: int
    """

    if isinstance(await run_query("INSERT INTO chat_members(chat, user_id) VALUES($1, $2);",
                                  "none",
                                  "one",
                                  chat_id,
                                  user_id), PostgresError):
        return False
    return True


async def get_chat_member(user_id: int, chat_id: int) -> Union[type(None), ChatMember, PostgresError]:
    """
    Retrieves a chat member from the database given its user ID and the
    chat's ID

    Returns None if either the chat or the user don't exist, a ChatMember object if they do
    or an exception if the query raised an error

    :param user_id: The user's ID
    :type user_id: int
    :param chat_id: The chat's ID
    :type chat_id: int
    """

    result = await run_query(f"SELECT * FROM chat_members WHERE chat = $1 AND user_id = $2 LIMIT 1;",
                             "one",
                             "one",
                             chat_id,
                             user_id)
    if not isinstance(result, (PostgresError, type(None))):
        result = ChatMember(*result)
    return result


async def update_chat_member(chat_id: int, user_id: int):
    """
    Updates (or inserts) a chat member into the database

    :param chat_id: The chat's ID
    :type chat_id: int
    :param user_id: The member's ID
    :type user_id: int
    """

    if not (chat := await get_chat(chat_id)):
        # If the result of get_user is falsey (and it is not an error) then we need to
        # insert the new chat entry
        await insert_chat_member(chat_id, user_id)
    elif not isinstance(chat, PostgresError):
        # Chat already exists, update it!
        await run_query("UPDATE chat_members SET user_id = $2 WHERE chat = $1",
                        "none",
                        "one",
                        chat_id,
                        user_id)
    else:
        # Error! There's nothing we can do, but run_query already
        # logged it so it's fine (ish)
        return
