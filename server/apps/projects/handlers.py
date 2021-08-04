import asyncpg.exceptions
from aiohttp import web

from server.apps.view import BaseHandler
from db.utils import from_record_to_dict
from db.tables.projects import (
    get_list_of_projects,
    get_project_by_id,
    add_new_project,
    patch_project,
    delete_project,
)


class CRUDProjectsViewHandler(BaseHandler):
    async def process_request(self, request: web.Request, *args, **kwargs):
        connection = await request.app['db'].acquire()
        query = dict(request.query)

        if request.method == 'GET':
            if not query:
                return from_record_to_dict(
                    await get_list_of_projects(request.app['db'])
                )

            pid = int(query.get('pid'))
            if pid:
                project_ = await get_project_by_id(request.app['db'], pid)
                if project_ is None:
                    msg = f'Project with id = {pid} does not exists.'
                    raise web.HTTPNotFound(reason=msg)
                else:
                    return from_record_to_dict(
                        await get_project_by_id(request.app['db'], pid)
                    )

            msg = 'Error request.'
            raise web.HTTPBadRequest(reason=msg)

        if request.method == 'POST':
            data = await request.json()
            try:
                new_pid = await add_new_project(connection, data)
            except asyncpg.exceptions.UniqueViolationError:
                msg = f'Project with name {data["name"]} is already exists.'
                raise web.HTTPBadRequest(reason=msg)

            status = str(web.HTTPCreated(reason='201'))

            return {'id': new_pid,
                    'name': data['name'],
                    'settings': data['settings'],
                    'status': status
                    }

        if request.method == 'PATCH':
            pid = int(query.get('pid'))
            data = await request.json()
            try:
                await patch_project(request.app['db'], pid, data)
            except asyncpg.exceptions.UniqueViolationError:
                msg = f'Project with name {data["name"]} is already exists.'
                raise web.HTTPBadRequest(reason=msg)

            if pid:
                project_ = await get_project_by_id(request.app['db'], pid)
                if project_ is None:
                    msg = f'Project with id = {pid} does not exists.'
                    raise web.HTTPNotFound(reason=msg)
                else:
                    status = str(web.HTTPSuccessful(reason='200'))
                    return {'id': pid,
                            'name': data['name'],
                            'settings': data['settings'],
                            'status': status
                            }

        if request.method == 'DELETE':
            query = dict(request.query)
            pid = int(query.get('pid'))

            if pid:
                project_ = await get_project_by_id(request.app['db'], pid)
                if project_ is None:
                    msg = f'Project with id = {pid} does not exists.'
                    raise web.HTTPNotFound(reason=msg)

            try:
                await delete_project(request.app['db'], pid)
            except asyncpg.exceptions.NoData:
                msg = f'Project with id {pid} does not exists.'
                raise web.HTTPNotFound(reason=msg)

            status = str(web.HTTPSuccessful(reason='200'))
            return {'status': status}
