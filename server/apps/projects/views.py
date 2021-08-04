import json

from aiohttp import web

from server.apps.view import BaseView
from server.apps.projects.handlers import CRUDProjectsViewHandler


class ProjectsCRUDView(BaseView):
    handler = CRUDProjectsViewHandler

    async def post(self):
        result = await self.handle()

        return web.json_response(result)

    async def get(self):
        result = await self.handle()

        return web.json_response(result)

    async def patch(self):
        result = await self.handle()

        return web.json_response(result)

    async def delete(self):
        result = await self.handle()

        return web.json_response(result)
