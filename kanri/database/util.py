from kanri import LOCAL
from kanri.database.users import get_user, insert_user


async def ensure_bot_in_db():
    """
    Makes sure that the bot is in the database by inserting it
    manually
    """

    if not (self := await get_user(by="id", term=LOCAL.bot_id)) and not isinstance(self, Exception):
        await insert_user(LOCAL.bot_id, LOCAL.bot_username)