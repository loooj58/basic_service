import asyncpg
import pytest
import sys
from typing import Any, Dict, List

from pg_db.database import PgDB




async def test_insert_data(pgdb: PgDB, conn):
    table_name = 'test_insert_data'
    await conn.fetch(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL
        );
    ''')
    records = [{'id': 3, 'name': 'Dog'}, {'id': 4, 'name': 'Frog'}]
    await pgdb.insert_data(table_name, records)
    await conn.fetch(f'DROP TABLE {table_name}')


@pytest.mark.parametrize(
    "limit,offset,true_res", [
        (0, 0, []),
        (1, 0, [{'id': 1, 'name': 'Dino'}]),
        (1, 2, [{'id': 3, 'name': 'Dog'}]),
        (2, 2, [{'id': 3, 'name': 'Dog'}, {'id': 4, 'name': 'Frog'}])
    ]
)
async def test_get_data(pgdb: PgDB, conn, limit: int, offset: int, true_res: List[Dict[str, Any]]):
    table_name = 'test_get_data'
    await conn.fetch(f'''
        CREATE TABLE {table_name} (
            id INT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL
        );
    ''')
    await conn.fetch(f'''INSERT INTO {table_name}
        (id, name)
        VALUES (1, 'Dino'), (2, 'Cat'), (3, 'Dog'), (4, 'Frog');''')
    res = await pgdb.get_data(table_name, offset, limit)
    await conn.fetch(f'DROP TABLE {table_name}')
    assert res == true_res


@pytest.mark.parametrize("id,true_res", [
    (1, {'id': 1, 'name': 'Dino'}),
    (2, {'id': 2, 'name': 'Cat'}),
    (3, {'id': 3, 'name': 'Dog'}),
    (4, {'id': 4, 'name': 'Frog'}),
    (5, {})
    ])
async def test_get_item(pgdb: PgDB, conn, id: int, true_res: Dict[str, Any]):
    table_name = 'test_get_item'
    await conn.fetch(f'''
        CREATE TABLE {table_name} (
            id INT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL
        );
    ''')
    await conn.fetch(f'''INSERT INTO {table_name}
        (id, name)
        VALUES (1, 'Dino'), (2, 'Cat'), (3, 'Dog'), (4, 'Frog');''')
    res = await pgdb.get_item(table_name, id)
    await conn.fetch(f'DROP TABLE {table_name}')
    assert res == true_res


@pytest.mark.parametrize("ids,conditions,values,true_res", [
    ([1], [{'id': 1}], [{'id': 1, 'name': 'Dino_updated'}], [{'id': 1, 'name': 'Dino_updated'}]),
    ([5], [{'name': 'Frog'}], [{'id': 5, 'name': 'Frog_updated'}], [{'id': 5, 'name': 'Frog_updated'}]),
    ([2, 4], [{'name': 'Cat'}], [{'name': 'Cat_updated'}], [{'id': 2, 'name': 'Cat_updated'}, {'id': 4, 'name': 'Cat_updated'}]),
    ([3], [{'id': 3, 'name': 'Dog'}], [{'id': 3, 'name': 'Dog_updated'}], [{'id': 3, 'name': 'Dog_updated'}]),
    ])
async def test_update_data(
        pgdb: PgDB, conn,
        conditions: Dict[str, Any], values: Dict[str, Any],
        ids:List[int], true_res: List[Dict[str, Any]]
    ):
    table_name = 'test_update_data'
    await conn.fetch(f'''
        CREATE TABLE {table_name} (
            id INT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL
        );
    ''')
    await conn.fetch(f'''INSERT INTO {table_name}
        (id, name)
        VALUES (1, 'Dino'), (2, 'Cat'), (3, 'Dog'), (4, 'Cat'), (5, 'Frog');''')
    await pgdb.update_data(table_name, conditions, values)
    for i, id in enumerate(ids):
        res = dict((await conn.fetch(f'''SELECT * FROM {table_name} WHERE id = {id}'''))[0])
        assert res == true_res[i]
    await conn.fetch(f'DROP TABLE {table_name}')
