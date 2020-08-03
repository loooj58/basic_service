from aiohttp import web
import asyncio

from pg_db.database import PgDB
from service.service_app import ServiceApp
from config import *


def main():
    loop = asyncio.get_event_loop()
    db = loop.run_until_complete(
        PgDB.create_PgDB(
            user=user, password=password,
            database=database, host=host,
            port=port
        )
    )
    service_app = ServiceApp(web.Application(), db)
    web.run_app(service_app.app, host='0.0.0.0', port=1234)


if __name__ == '__main__':
    main()
