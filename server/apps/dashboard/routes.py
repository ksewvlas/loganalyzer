from aiohttp import web

from server.apps.dashboard.views import ShowDashboardView

PREFIX = '/dashboard/'

routes = [
    web.get(PREFIX, ShowDashboardView),
]
