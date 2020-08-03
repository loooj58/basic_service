from aiohttp import web
from dicttoxml import dicttoxml
import json
import logging
from typing import Any

from service.base_db import BaseDB


class Response:
    def __init__(self, is_ok: bool, data: Any = None):
        self.is_ok = is_ok
        self.data = data

    def response(self, format='json'):
        assert format in ('json', 'xml')
        resp = {
            'status': 'ok' if self.is_ok else 'error',
            'body': self.data
        }
        return web.Response(
            text=json.dumps(resp) if format == 'json' else str(dicttoxml(resp))
        )


class ServiceApp:
    def __init__(self, app: web.Application, db: BaseDB):
        self.app = app
        self.db = db
        self.app.add_routes([web.get('/get_data/{table_name}/limit/{limit}/offset/{offset}', self.get_data)])
        self.app.add_routes([web.get('/get_item/{table_name}/{id}/{format}', self.get_item)])
        self.app.add_routes([web.post('/insert_data', self.insert_data)])
        self.app.add_routes([web.post('/update_data', self.update_data)])

    async def insert_data(self, request):
        data = await request.json()
        for table_name, records in data.items():
            await self.db.insert_data(table_name, records)
        return Response(True).response()

    async def update_data(self, request):
        data = await request.json()
        for table_name, info in data.items():
            assert len(info['conditions']) == len(info['values'])
            await self.db.update_data(table_name, info['conditions'], info['values'])
        return Response(True).response()

    async def get_data(self, request):
        table_name = request.match_info['table_name']
        offset = int(request.match_info['offset'])
        limit = int(request.match_info['limit'])
        data = await self.db.get_data(table_name, offset, limit)
        return Response(True, data).response()

    async def get_item(self, request):
        table_name = request.match_info['table_name']
        format = request.match_info['format']
        id = int(request.match_info['id'])
        item = await self.db.get_item(table_name, id)
        return Response(True, item).response(format=format)
