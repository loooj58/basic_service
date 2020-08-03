import asyncio
import asyncpg
import sys
from textwrap import dedent

from service.base_db import BaseDB, SubTable, Record


class DollarInserter:
    def __init__(self):
        self.vals = []
        self.cntr = 0
    
    def __call__(self, val):
        self.vals.append(val)
        self.cntr += 1
        return f'${self.cntr}'


class PgDB(BaseDB):

    def __init__(self, conn):
        self.conn = conn

    @classmethod
    async def create_PgDB(
        cls,
        user: str = 'user',
        password: str = 'password',
        database: str = 'database',
        host: str = '127.0.0.1',
        port: int = 5432
    ):
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port
        )
        return cls(conn)

    async def insert_data(
        self,
        table_name: str,
        records: SubTable
    ) -> None:
        if len(records) == 0:
            return

        record_keys = list(records[0].keys())
        columns = ', '.join(records[0].keys())
        req = dedent(f'''
                INSERT INTO {table_name}
                ({columns})
                VALUES\n
        ''')

        all_data = []
        for record in records:
            all_data.extend(list(record.values()))
        
        vals = [
            list(range(i * len(record_keys) + 1, (i + 1) * len(record_keys) + 1))
            for i in range(len(records))
        ]

        req += ',\n'.join(
            '(' + ', '.join(f'${x}' for x in rec) + ')'
            for rec in vals
        )

        await self.conn.execute(req, *all_data)

    async def get_data(
        self,
        table_name: str,
        offset: int,
        limit: int
    ) -> SubTable:
        req = f'''SELECT * FROM {table_name}
            OFFSET {offset} LIMIT {limit}'''
        records = await self.conn.fetch(req)
        records_dict = [dict(record) for record in records]
        return records_dict

    async def update_data(
        self,
        table_name: str,
        conditions: SubTable,
        values: SubTable
    ) -> None:
        assert len(conditions) == len(values)
        for condition, value in zip(conditions, values):
            dollar_inserter = DollarInserter()
            condition = ' AND '.join(f'{cond} = {dollar_inserter(val)}' for cond, val in condition.items())
            value = ', '.join(f'{name} = {dollar_inserter(val)}' for name, val in value.items())
            req = dedent(f'''
                UPDATE  {table_name}
                SET {value}
                WHERE {condition}'''
            )
            await self.conn.execute(req, *dollar_inserter.vals)

    async def get_item(
        self,
        table_name: str,
        id: int
    ) -> Record:
        req = f'''SELECT * FROM {table_name}
            WHERE id = {id}'''
        records = await self.conn.fetch(req)
        if len(records) == 0:
            return {}
        record = records[0]
        record_dict = dict(record)
        return record_dict
