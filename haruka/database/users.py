from typing import Optional, Union, List
from asyncpg.exceptions import PostgresError
from haruka.database.chats import get_chat, insert_chat
from haruka.database import User, ChatMember, Chat, run_query
from haruka.database.chat_member import get_chat_member, insert_chat_member


async def get_user(by: str, term: Union[str, int]) -> Union[User, type(None), PostgresError]:
    """
    Fetches a user from the database either by ID or by username.
    Returns None if the user doesn't exist, a User object if it does
    or an exception if the query raised an error

    :param by: The search mode, either "id" or "username"
    :type by: str
    :param term: The search term (either an ID or a string according
    to the by parameter)
    """

    result = await run_query(f"SELECT * FROM users WHERE {'user_id' if by == 'id' else 'username'} = $1 LIMIT 1;",
                             "one",
                             "one",
                             term)
    if not isinstance(result, (PostgresError, type(None))):
        result = User(*result)
    return result


async def insert_user(user_id: int, username: Optional[str] = None):
    """
    Inserts a user in the database. Returns True on success and False
    upon failure

    :param user_id: The user's ID
    :type user_id: int
    :param username: The user's username, if present, defaults to None
    :type username: str, optional
    """

    if isinstance(await run_query("INSERT INTO users(user_id, username) VALUES($1, $2);",
                                  "none",
                                  "one",
                                  user_id,
                                  username), PostgresError):
        return False
    return True


async def update_user(user_id: int, username: Optional[str], chat_id: Optional[int] = None,
                      chat_name: Optional[str] = None):
    """
    Updates (or inserts) a user entry in the database, optionally
    binding it to a specific chat (if, for instance, the user was
    met in a group)

    :param user_id: The user's ID
    :type user_id: int
    :param username: The user's username, if present, defaults to None
    :type username: str, optional
    :param chat_id: The chat id in which the user was met, defaults to None
    :type chat_id: optional, int
    :param chat_name: The name of the chat where the user was met, defaults to None
    :type chat_name: optional, str
    """

    if not (user := await get_user(by="id", term=user_id)):
        # If the result of get_user is falsey (and it is not an error) then we need to
        # insert the new user entry
        await insert_user(user_id, username)
    elif not isinstance(user, PostgresError):
        # User already exists, update it!
        await run_query("UPDATE users SET username = $2 WHERE user_id = $1",
                        "none",
                        "one",
                        user_id,
                        username)
    else:
        # Error! There's nothing we can do, but run_query already
        # logged it so it's fine (ish)
        return
    if not chat_id:
        # If the user was not met in a group, then we bail out
        # since our work is done
        return
    if not await get_chat(chat_id):
        # If the user was indeed met in a chat, we make sure
        # it's there to insert our ChatMember later
        await insert_chat(chat_id, chat_name)
    if not await get_chat_member(user_id, chat_id):
        # Finally, if the user isn't in the given chat,
        # we add it
        await insert_chat_member(user.user_id, chat_id)


async def get_chat_members(chat_id: int) -> Union[type(None), List[ChatMember], PostgresError]:
    """
    Gets all the chat members given a chat_id. Returns
    None if the given chat doesn't exist, a list of
    ChatMember objects

    :param chat_id: The ID of the chat
    :type chat_id: int
    """

    chat_members = []
    result = await run_query("SELECT * FROM chat_members WHERE chat_id = $1;",
                             "all",
                             "one",
                             chat_id)
    if not result or not isinstance(result, PostgresError):
        # We can only do something if an error didn't occur!
        for chat_member in result:
            chat_members.append(ChatMember(*chat_member))
    else:
        return result


async def get_all_chats() -> Union[type(None), List[Chat], PostgresError]:
    """
    Gets all the chats registered in the database
    """

    chats = []
    result = await run_query("SELECT * FROM chats;",
                             "all",
                             "one")
    if not result or not isinstance(result, PostgresError):
        # We can only do something if an error didn't occur!
        for chat in result:
            chats.append(Chat(*chat))
    else:
        return result


async def get_all_users() -> Union[type(None), List[User], PostgresError]:
    """
    Gets all the users registered in the database
    """

    users = []
    result = await run_query("SELECT * FROM users;",
                             "all",
                             "one")
    if not result or not isinstance(result, PostgresError):
        # We can only do something if an error didn't occur!
        for user in result:
            users.append(User(*user))
    else:
        return result


async def get_user_num_chats(user_id: int) -> Union[type(None), List[User], PostgresError]:
    """
    Gets the number of chats where the user is present

    :param user_id: The ID of the user for which the count has to be performed
    :type user_id: int
    """

    return await run_query("SELECT COUNT(*) FROM chat_members WHERE user_id = $1",
                           "one",
                           "one",
                           user_id)


async def get_user_chats(user_id: int) -> Union[type(None), List[Chat], PostgresError]:
    """
    Gets all the chat_ids of the chats where the given user_id is
    present

    :param user_id: The user ID
    """

    try:
        chat_members = (
            SESSION.query(ChatMembers).filter(ChatMembers.user == int(user_id)).all()
        )
        return [i.chat for i in chat_members]
    finally:
        SESSION.close()


def num_chats():
    try:
        return SESSION.query(Chats).count()
    finally:
        SESSION.close()


def num_users():
    try:
        return SESSION.query(Users).count()
    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Chats).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)
            SESSION.add(chat)

        SESSION.flush()

        chat_members = (
            SESSION.query(ChatMembers)
                .filter(ChatMembers.chat == str(old_chat_id))
                .all()
        )
        for member in chat_members:
            member.chat = str(new_chat_id)
            SESSION.add(member)

        SESSION.commit()


def del_user(user_id):
    with INSERTION_LOCK:
        curr = SESSION.query(Users).get(user_id)
        if curr:
            SESSION.delete(curr)
            SESSION.commit()
            return True

        ChatMembers.query.filter(ChatMembers.user == user_id).delete()
        SESSION.commit()
        SESSION.close()
    return False


def rem_chat(chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Chats).get(str(chat_id))
        if chat:
            SESSION.delete(chat)
            SESSION.commit()
        else:
            SESSION.close()
