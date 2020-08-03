from aiohttp import web
from copy import deepcopy
import json
import pytest

from service.service_app import ServiceApp


@pytest.mark.parametrize(
    "limit,offset", [
        (0, 0), (0, 1), (1, 2), (2, 2)
    ]
)
async def test_get_data(limit, offset, service_app, aiohttp_client):
    client = await aiohttp_client(service_app.app)
    resp = await client.get(f'/get_data/users/limit/{limit}/offset/{offset}')
    assert resp.status == 200
    text = await resp.text()
    data = json.loads(text)
    assert data['status'] == 'ok'
    users_num = len(service_app.db.data['users'])
    assert len(data['body']) == min(users_num - offset, limit)


@pytest.mark.parametrize("id", [1, 2])
async def test_get_item_json(id, service_app, aiohttp_client):
    client = await aiohttp_client(service_app.app)
    resp = await client.get(f'/get_item/users/{id}/json')
    assert resp.status == 200
    text = await resp.text()
    data = json.loads(text)
    assert data['status'] == 'ok'
    assert data['body'] == service_app.db.data['users'][id - 1]


async def test_insert_data(db, aiohttp_client):
    db = deepcopy(db)
    service_app = ServiceApp(web.Application(), db)
    client = await aiohttp_client(service_app.app)
    data_to_insert = {
        'some_table': [{'key1': 'value1', 'key2': 'value2'}],
        'some_table2': [{'key3': 'value3', 'key4': 'value4'}]
    }
    resp = await client.post(f'/insert_data', json=data_to_insert)
    assert resp.status == 200
    text = await resp.text()
    data = json.loads(text)
    assert data['status'] == 'ok'

    first_inserted_table = db.insert_log[0][0]
    assert first_inserted_table in data_to_insert
    assert db.insert_log[0][1] == data_to_insert[first_inserted_table]

    second_inserted_table = db.insert_log[1][0]
    assert second_inserted_table in data_to_insert
    assert db.insert_log[1][1] == data_to_insert[second_inserted_table]

    assert first_inserted_table != second_inserted_table


async def test_update_data(db, aiohttp_client):
    db = deepcopy(db)
    service_app = ServiceApp(web.Application(), db)
    client = await aiohttp_client(service_app.app)
    data_to_update = {
        'some_table': {'conditions': [{'id': 1}, {'id': 3}], 'values': [{'name': 'Dino'}, {'name': 'Cat'}]},
        'some_table2': {'conditions': [{'id': 2}, {'id': 4}], 'values': [{'name': 'Rrrr'}, {'name': 'Meow'}]}
    }
    resp = await client.post(f'/update_data', json=data_to_update)
    assert resp.status == 200
    text = await resp.text()
    data = json.loads(text)
    assert data['status'] == 'ok'

    first_updated_table = db.update_log[0][0]
    assert first_updated_table in data_to_update
    assert db.update_log[0][1] == data_to_update[first_updated_table]['conditions']
    assert db.update_log[0][2] == data_to_update[first_updated_table]['values']

    second_updated_table = db.update_log[1][0]
    assert second_updated_table in data_to_update
    assert db.update_log[1][1] == data_to_update[second_updated_table]['conditions']
    assert db.update_log[1][2] == data_to_update[second_updated_table]['values']

    assert first_updated_table != second_updated_table
