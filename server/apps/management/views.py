from aiohttp import web

import server.apps.management.handlers as handlers
from server.apps.view import BaseView


class RunProjectStreamView(BaseView):
    handler = handlers.RunProjectStreamingHandler

    async def get(self):
        data = await self.handle()

        return web.json_response(data)


class StopProjectStreamView(BaseView):
    handler = handlers.StopProjectStreamingHandler

    async def get(self):
        data = await self.handle()

        return web.json_response(data)
