import pytest
import asyncio

import testing.postgresql as database

from asyncpgsa import create_pool

from db import create_alchemy_engine
from db.tables import metadata


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def pg_pool(event_loop):
    with database.Postgresql() as db:
        dsn = db.dsn()
        dsn['db'] = dsn.pop('database')
        engine = create_alchemy_engine(dsn)

        metadata.drop_all(engine)
        metadata.create_all(engine)

        yield await create_pool(**db.dsn())
