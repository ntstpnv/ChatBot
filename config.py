from os import getenv

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


load_dotenv()

TOKEN = getenv("token")

DB_USER = getenv("db_user", "postgres")
DB_PASS = getenv("db_pass", "postgres")
DB_HOST = getenv("db_host", "localhost")
DB_PORT = getenv("db_port", "5432")
DB_NAME = getenv("db_name", "postgres")

DSN = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

ASYNC_ENGINE = create_async_engine(DSN)

ASYNC_SESSION = async_sessionmaker(ASYNC_ENGINE)
