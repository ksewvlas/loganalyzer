from typing import Dict, Any

import psycopg2
from asyncpgsa import create_pool
from asyncpgsa.connection import SAConnection
from asyncpg.pool import Pool
from aiohttp.web import Application
from sqlalchemy import create_engine

__all__ = [
    'pg_pool',
    'pg_close',
    'create_pg_pool',
    'create_psycopg_connection',
    'create_alchemy_engine',
]


async def create_pg_pool(db_config: dict) -> Pool:
    return await create_pool(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['db'],
        user=db_config['user'],
        password=db_config['password'],
        min_size=db_config['min_size'],
        max_size=db_config['max_size'],
        connection_class=SAConnection,
    )


async def pg_pool(app: Application):
    db_config = app['config']['postgres']
    app['db'] = await create_pg_pool(db_config)


async def pg_close(app: Application):
    await app['db'].close()


def create_psycopg_connection(db_conf: Dict[str, Any]):
    return psycopg2.connect(
        dbname=db_conf['database'],
        port=db_conf['port'],
        user=db_conf['user'],
        host=db_conf['host'],
        password=db_conf.get('password'),
    )


def make_dsn_from_conf(db_conf: Dict[str, Any]):
    return 'postgresql://%s:%s@%s:%s/%s' % (
        db_conf['user'], db_conf.get('password'), db_conf['host'], db_conf['port'], db_conf['db'])


def create_alchemy_engine(db_conf: Dict[str, Any]):
    return create_engine(
        make_dsn_from_conf(db_conf)
    )
