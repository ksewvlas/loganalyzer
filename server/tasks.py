import asyncio

from streaming.streaming import SFTPAccessLogStreaming
from db.tables.projects import get_list_of_projects


async def check_streams_status(app):
    while True:
        stopped = []
        streams = app['streams'][:]

        for stream in streams:
            if not stream.is_alive or stream.stopped:
                stopped.append(stream)

        for stream in stopped:
            app['streams'].remove(stream)

        await asyncio.sleep(1)


async def run_streams(app):
    async with app['db'] as connection:
        projects = await get_list_of_projects(connection)

    streams = [
        SFTPAccessLogStreaming(
            config=app['config'],
            project_id=project['id'],
        )
        for project in projects
    ]

    app['streams'] = streams

    for stream in streams:
        stream.start()


async def start_background_tasks(app):
    if app['params']['start_streams']:
        asyncio.create_task(run_streams(app))

    asyncio.create_task(check_streams_status(app))
