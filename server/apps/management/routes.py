from aiohttp import web

from server.apps.management.views import RunProjectStreamView, StopProjectStreamView

PREFIX = '/management/'

routes = [
    web.view(PREFIX + 'run/', RunProjectStreamView),
    web.view(PREFIX + 'stop/', StopProjectStreamView),
]
