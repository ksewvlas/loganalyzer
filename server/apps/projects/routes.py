from aiohttp import web

from server.apps.projects.views import ProjectsCRUDView

PREFIX = '/projects/'

routes = [
    web.view(PREFIX, ProjectsCRUDView),
]
