import pytest

from db.tables.projects import (
    get_project_by_id,
    get_list_of_projects,
    add_new_project,
    patch_project,
    delete_project,
)
from db.tables.logs import (
    get_logs_by_project_id,
    analyze_logs,
)
from db.utils import from_record_to_dict

pytestmark = pytest.mark.asyncio


async def test_get_project_by_id(pg_pool):
    connection = await pg_pool.acquire()
    id_ = await connection.fetchval(
        'insert into projects(id, name, settings, created_at) '
        'values (1, \'test\', \'{}\', \'2021-01-01\')'
        'returning id'
    )

    result = dict(await get_project_by_id(connection, id_))

    assert dict(result) == {
        'id': 1,
        'name': 'test',
        'settings': '{}',
        'created_at': '2021-01-01'
    }


async def test_get_list_of_projects(pg_pool):
    connection = await pg_pool.acquire()
    await connection.execute(
        'insert into projects(id, name, settings, created_at) '
        'values '
        '(1, \'test\', \'{}\', \'2021-01-01\'),'
        '(2, \'test2\', \'{"test": "test"}\', \'2021-01-02\')'
    )

    result = await get_list_of_projects(connection)

    assert from_record_to_dict(result) == [
        {
            'id': 1,
            'name': 'test',
            'settings': '{}',
            'created_at': '2021-01-01',
        },
        {
            'id': 2,
            'name': 'test2',
            'settings': '{"test": "test"}',
            'created_at': '2021-01-02',
        },
    ]


async def test_add_new_project(pg_pool):
    data = {
        'id': 1,
        'name': 'test',
        'settings': {},
        'created_at': '2021-12-12'
    }

    connection = await pg_pool.acquire()
    await add_new_project(connection, data)

    result = dict(await get_project_by_id(connection, data['id']))
    data['settings'] = str(data['settings'])

    assert dict(result) == data


async def test_patch_project(pg_pool):
    connection = await pg_pool.acquire()

    id_ = await connection.fetchval(
        'insert into projects(id, name, settings, created_at) '
        'values (1, \'test\', \'{}\', \'2021-01-01\')'
        'returning id'
    )

    await patch_project(
        connection, id_, {'name': 'new', 'settings': {'test': 'test'}}
    )
    result = dict(await get_project_by_id(connection, id_))

    assert result == {
        'id': 1,
        'name': 'new',
        'settings': '{"test": "test"}',
        'created_at': '2021-01-01'
    }


async def test_delete_project(pg_pool):
    connection = await pg_pool.acquire()
    id_ = await connection.fetchval(
        'insert into projects(id, name, settings, created_at) '
        'values (1, \'test\', \'{}\', \'2021-01-01\')'
        'returning id'
    )

    await delete_project(connection, id_)

    result = await get_project_by_id(connection, id_)

    assert result is None


async def test_get_logs_by_project_id(pg_pool):
    connection = await pg_pool.acquire()
    pid = await connection.fetchval(
        'insert into projects(id, name, settings, created_at) '
        'values (1, \'test\', \'{}\', \'2021-01-01\')'
        'returning id'
    )

    await connection.execute(
        f'insert into logs(id, remote_addr, status, created_at, project_id) '
        f'values'
        f'(1, \'127.0.0.1\', 200, \'2021-01-01\', {pid}),'
        f'(2, \'127.0.0.1\', 400, \'2021-01-01\', {pid}),'
        f'(3, \'127.0.0.1\', 500, \'2021-01-01\', {pid})'
    )

    result = from_record_to_dict(
        await get_logs_by_project_id(connection, pid)
    )

    benchmark = [
        {
            'id': 1,
            'remote_addr': '127.0.0.1',
            'remote_user': None,
            'time_local': None,
            'request': None,
            'status': 200,
            'body_bytes_sent': None,
            'http_referer': None,
            'http_user_agent': None,
            'created_at': '2021-01-01 00:00:00',
            'project_id': 1
        },
        {
            'id': 2,
            'remote_addr': '127.0.0.1',
            'remote_user': None,
            'time_local': None,
            'request': None,
            'status': 400,
            'body_bytes_sent': None,
            'http_referer': None,
            'http_user_agent': None,
            'created_at': '2021-01-01 00:00:00',
            'project_id': 1
        },
        {
            'id': 3,
            'remote_addr': '127.0.0.1',
            'remote_user': None,
            'time_local': None,
            'request': None,
            'status': 500,
            'body_bytes_sent': None,
            'http_referer': None,
            'http_user_agent': None,
            'created_at': '2021-01-01 00:00:00',
            'project_id': 1
        }]

    assert result == benchmark


async def test_analyze_logs(pg_pool):
    connection = await pg_pool.acquire()
    pid = await connection.fetchval(
        'insert into projects(id, name, settings, created_at) '
        'values (1, \'test\', \'{}\', \'2021-01-01\')'
        'returning id'
    )

    await connection.execute(
        f'insert into logs'
        f'(id, remote_addr, status, body_bytes_sent, http_referer, time_local, project_id) '
        f'values'
        f'(1, \'127.0.0.1\', 200, 100, \'test1.com\', \'2021-01-01\', {pid}),'
        f'(2, \'127.0.0.2\', 400, 200, \'test2.com\', \'2021-01-02\', {pid}),'
        f'(3, \'127.0.0.3\', 500, 300, \'test3.com\', \'2021-01-03\', {pid})'
    )

    result = await analyze_logs(connection, pid)

    benchmark = {
        'total_requests': 3,
        'unique_users': 3,
        'referrers': 3,
        'total_bytes_sent': 600,
        'grouped_by_statuses': [
            {
                'project_id': 1,
                'status': 200,
                'unique_users': 1,
                'total_bytes_sent': 100,
                'total_requests': 1,
                'referrers': 1,
            },
            {
                'project_id': 1,
                'status': 400,
                'unique_users': 1,
                'total_bytes_sent': 200,
                'total_requests': 1,
                'referrers': 1,
            },
            {
                'project_id': 1,
                'status': 500,
                'unique_users': 1,
                'total_bytes_sent': 300,
                'total_requests': 1,
                'referrers': 1,
            }
        ],
    }

    assert result == benchmark
