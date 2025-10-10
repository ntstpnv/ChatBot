from collections import namedtuple
from dotenv import load_dotenv
from os import getenv

from sqlalchemy.ext.asyncio import create_async_engine


load_dotenv()


DB_USER = getenv("db_user")
DB_PASS = getenv("db_pass")
DB_HOST = getenv("db_host")
DB_PORT = getenv("db_port")
DB_NAME = getenv("db_name")

DSN = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


CONFIG = namedtuple(
    "Config",
    [
        "TOKEN",
        "ASYNC_ENGINE",
    ],
)(
    getenv("token"),
    create_async_engine(DSN),
)
