from aiohttp import web

from db.tables.projects import get_project_by_id
from db.tables.logs import analyze_logs, get_logs_by_project_id
from server.apps.view import BaseHandler


class ShowDashboardHandler(BaseHandler):

    async def process_request(self, request: web.Request, *args, **kwargs):
        data = dict(request.query)
        pid = int(data['pid'])

        project = await get_project_by_id(request.app['db'], pid)

        if not project:
            raise web.HTTPNotFound(reason=f'Project {pid} not found.')

        analytics = await analyze_logs(request.app['db'], project_id=pid)
        logs = await get_logs_by_project_id(request.app['db'], project_id=pid, )

        return analytics, logs
