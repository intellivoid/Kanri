import asyncpg
from haruka import LOCAL
from dataclasses import dataclass, field
from asyncpg.exceptions import PostgresError
from typing import Optional, Union, Dict, Iterable


DB_SCHEMA = r"""
CREATE TABLE IF NOT EXISTS users(
    uid BIGINT GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT UNIQUE NOT NULL,
    username CHARACTER VARYING(32) NULL,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY(user_id));

CREATE TABLE IF NOT EXISTS chats(
    uid BIGINT GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    chat_name TEXT NOT NULL,
    PRIMARY KEY(chat_id));

CREATE TABLE IF NOT EXISTS chat_members(
    chat BIGINT NOT NULL REFERENCES chats(chat_id) ON UPDATE CASCADE ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY(chat));

CREATE TABLE IF NOT EXISTS chat_settings(
    chat_id BIGINT NOT NULL REFERENCES chats(chat_id) ON UPDATE CASCADE ON DELETE CASCADE,
    antispam_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    nlp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    welcome_message TEXT NULL DEFAULT NULL,
    antiflood_parameters TEXT NOT NULL DEFAULT '{"sensibility": 1, "threshold": 4, "percentage": 75, "delete": false, 
    "ban": 30, "notice": "", "enabled": true}');

CREATE TABLE IF NOT EXISTS filters(
    chat_id BIGINT NOT NULL REFERENCES chats(chat_id) ON UPDATE CASCADE ON DELETE CASCADE,
    trigger CHARACTER VARYING(4096) NOT NULL,
    reply CHARACTER VARYING(4096) NOT NULL);

CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    reports_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_connected_chat BIGINT NULL REFERENCES chats(chat_id)
    );
"""


# Some handy wrappers around our database objects

@dataclass
class User:
    """
    A Telegram User
    """

    uid: int
    user_id: int
    username: Optional[str] = None
    deleted: Optional[bool] = False


@dataclass
class Chat:
    """
    A Telegram chat
    """

    uid: int
    chat_id: int


@dataclass
class ChatMember:
    """
    A Telegram Chat member (as per our database schema)
    """

    chat_id: int
    user_id: int


@dataclass
class ChatSettings:
    """
    A wrapper around the settings of a chat
    """

    chat_id: int
    antispam_enabled: Optional[bool] = False
    nlp_enabled: Optional[bool] = False
    welcome_message: Optional[str] = None
    antiflood_parameters: Optional[Dict[str, Union[bool, int, str]]] = field(default_factory=dict(**{
        "sensibility": 1,
        "threshold": 4,
        "percentage": 75,
        "delete": False,
        "ban": 30,
        "notice": "",
        "enabled": True}))


@dataclass
class Filters:
    """
    A wrapper around chat filters
    """

    chat_id: int
    trigger: str
    reply: str


@dataclass
class UserSettings:
    """
    A wrapper around user-wise settings
    """

    user_id: int
    reports_enabled: Optional[bool] = True
    last_connected_chat: Optional[int] = None


async def init_database(min_size: Optional[int] = 1, max_size: Optional[int] = 2) -> asyncpg.pool.Pool:
    """
    Initializes the PostgreSQL database by executing
    the schema query and returns an initialized pool object

    :param min_size: The minimum size of the connection pool, defaults to 1
    :type min_size: int, optional
    :param max_size: The maximum size of the connection pool, defaults to 2
    :type max_size: int, optional
    :returns: :class: asyncpg.pool.Pool
    """

    pool = await asyncpg.create_pool(LOCAL.DB_URI, min_size=min_size, max_size=max_size)
    async with pool.acquire() as conn:
        await conn.execute(DB_SCHEMA)
    return pool


async def run_query(query: str, fetch: str, mode: str, *args) -> Union[type(None), PostgresError, Iterable]:
    """
    Runs an SQL query on the database and optionally fetches the result.
    Any extra positional arguments are safely interpolated into the query itself

    :param query: The query to be executed
    :type query: str
    :param fetch: The kind of fetching to perform. Can be "one", "all" or "none"
    :type fetch: str
    :param mode: The query execution mode. Can be "one" or "many"
    :returns: None if the query didn't return any output, the result(s) of the query
        if it did and an exception object if an error occurred
    """

    try:
        async with LOCAL.database_pool.acquire() as connection:
            if mode == "one":
                if fetch == "none":
                    await connection.execute(query, *args)
                elif fetch == "one":
                    return await connection.fetchrow(query, *args)
                else:
                    return await connection.fetch(query, *args)
            else:
                if fetch == "none":
                    await connection.executemany(query, *args)
                else:
                    raise ValueError(f"Cannot run a query in mode '{mode}' and fetch mode '{fetch}'")
    except PostgresError as psql_error:
        LOCAL.LOGGER.error(f"A fatal error occurred while running a query -> {type(psql_error).__name__}: {psql_error}")
        return psql_error