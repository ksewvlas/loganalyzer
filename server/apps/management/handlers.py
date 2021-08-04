from aiohttp import web

from server.apps.view import BaseHandler
from streaming import SFTPAccessLogStreaming


class RunProjectStreamingHandler(BaseHandler):

    async def process_request(self, request: web.Request, *args, **kwargs):
        query = dict(request.query)
        pid = query.get('pid')

        for stream in request.app['streams']:
            if stream.pid == pid and stream.is_alive():
                raise web.HTTPBadRequest(
                    reason='The streaming for this project is already working',
                )

        stream = SFTPAccessLogStreaming(
            config=request.app['config'],
            project_id=pid,
        )

        request.app['streams'].append(stream)

        stream.start()

        return {'result': 'ok'}


class StopProjectStreamingHandler(BaseHandler):

    async def process_request(self, request: web.Request, *args, **kwargs):
        query = dict(request.query)
        pid = query.get('pid')
        _stream = None

        for stream in request.app['streams']:
            if stream.pid == pid:
                _stream = stream

        if _stream:
            _stream.stop()
            request.app['streams'].remove(_stream)
        else:
            raise web.HTTPBadRequest(
                reason='Stream with this pid is not found in running streams',
            )

        return {'result': 'ok'}
