from aiohttp import web
from copy import deepcopy
import pytest

from service.service_app import ServiceApp
from service.base_db import BaseDB


class MockDB(BaseDB):
    def __init__(self, data):
        self.data = data
        self.insert_log = []
        self.update_log = []

    async def insert_data(self, table_name, records):
        self.insert_log.append((table_name, records))

    async def get_data(self, table_name, offset, limit):
        return self.data[table_name][offset: offset + limit]

    async def update_data(self, table_name, conditions, values):
        self.update_log.append((table_name, conditions, values))

    async def get_item(self, table_name, id):
        table = self.data[table_name]
        records = [r for r in table if r['id'] == id]
        assert len(records) == 1
        return records[0]


@pytest.fixture
def db():
    data = {
        'users': [
            {'id': 1, 'name': 'Dinosaur'},
            {'id': 2, 'name': 'Kitty'},
        ]
    }
    return MockDB(data)


@pytest.fixture
def service_app(db):
    db = deepcopy(db)
    return ServiceApp(web.Application(), db)
