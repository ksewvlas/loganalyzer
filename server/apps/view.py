import abc
from typing import Type

from aiohttp import web


class BaseHandler(abc.ABC):
    async def process_request(self, request: web.Request, *args, **kwargs):
        raise NotImplementedError('Processing of request is not implemented')


class BaseView(web.View, abc.ABC):
    handler: Type[BaseHandler] = None

    async def handle(self):
        return await self.handler().process_request(self.request)
