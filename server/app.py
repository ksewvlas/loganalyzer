from aiohttp import web

from db import pg_pool, pg_close
from server.apps.routes import routes
from server.tasks import start_background_tasks

__all__ = ['init_application']


def init_application(config):
    app = web.Application()

    app['config'] = config
    app['streams'] = []

    app.on_startup.append(pg_pool)
    app.on_startup.append(start_background_tasks)

    app.on_cleanup.append(pg_close)

    app.add_routes(routes)

    return app
