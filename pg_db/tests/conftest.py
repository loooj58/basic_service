import asyncio
import asyncpg
import pytest

from pg_db.database import PgDB


@pytest.yield_fixture
async def conn(loop):
    user = 'user'
    password = 'password'
    database = 'database'
    host = '127.0.0.1'
    port = 5432
    conn = await asyncpg.connect(user=user, password=password,
                                 database=database, host=host, port=port)
    yield conn
    await conn.close()


@pytest.fixture
async def pgdb(conn):
    return PgDB(conn)
