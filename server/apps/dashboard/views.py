from aiohttp import web

from server.apps.view import BaseView
from server.apps.dashboard.handlers import ShowDashboardHandler


class ShowDashboardView(BaseView):
    handler = ShowDashboardHandler

    async def get(self):
        data = await self.handle()

        return web.json_response(data)
