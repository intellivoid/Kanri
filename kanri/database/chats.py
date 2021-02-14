from typing import Union
from asyncpg.exceptions import PostgresError
from kanri.database import Chat, run_query


async def get_chat(chat_id: int) -> Union[type(None), Chat, PostgresError]:
    """
    Retrieves a chat from the database given its chat ID

    Returns None if the chat doesn't exist, a Chat object if it does
    or an exception if the query raised an error

    :param chat_id: The chat's ID
    """

    result = await run_query(f"SELECT * FROM chats WHERE chat_id = $1 LIMIT 1;",
                             "one",
                             "one",
                             chat_id)
    if not isinstance(result, (PostgresError, type(None))):
        result = Chat(*result)
    return result


async def insert_chat(chat_id: int, chat_title: str):
    """
    Inserts a chat in the database. Returns True on success and False
    upon failure

    :param chat_id: The chat's ID
    :type chat_id: int
    :param chat_title: The chat's name
    :type chat_title: str
    """

    if isinstance(await run_query("INSERT INTO chats(chat_id, chat_name) VALUES($1, $2);",
                                  "none",
                                  "one",
                                  chat_id,
                                  chat_title), PostgresError):
        return False
    return True


async def update_chat(chat_id: int, chat_title: str):
    """
    Updates (or inserts) a chat into the database

    :param chat_id: The chat's ID
    :type chat_id: int
    :param chat_title: The new chat's name
    :type chat_title: str
    """

    if not (chat := await get_chat(chat_id)):
        # If the result of get_user is falsey (and it is not an error) then we need to
        # insert the new chat entry
        await insert_chat(chat_id, chat_title)
    elif not isinstance(chat, PostgresError):
        # Chat already exists, update it!
        await run_query("UPDATE chats SET chat_name = $2 WHERE chat_id = $1",
                        "none",
                        "one",
                        chat_id,
                        chat_title)
    else:
        # Error! There's nothing we can do, but run_query already
        # logged it so it's fine (ish)
        return
