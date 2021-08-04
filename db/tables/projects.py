from typing import Dict, Any

import sqlalchemy as sa
from sqlalchemy.sql import func, select
from asyncpg import Connection, Record

from db.tables import metadata


projects = sa.Table(
    'projects',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('name', sa.String, nullable=False, unique=True),
    sa.Column('settings', sa.JSON, nullable=False),
    sa.Column('created_at', sa.DateTime, nullable=False, server_default=func.now())
)


async def get_project_by_id(connection: Connection, pk: int) -> Record:
    query = select(
        [
            projects.c.id,
            projects.c.name,
            projects.c.settings,
            sa.cast(projects.c.created_at, sa.String).label('created_at'),
        ]
    ).where(projects.c.id == pk)

    return await connection.fetchrow(query)


async def get_list_of_projects(connection: Connection):
    query = select(
        [
            projects.c.id,
            projects.c.name,
            projects.c.settings,
            sa.cast(projects.c.created_at, sa.String).label('created_at'),
        ]
    )

    return await connection.fetch(query)


async def add_new_project(connection: Connection, data: Dict[str, Any]) -> Record:
    query = projects.insert().values(**data).returning(projects.c.id)

    return await connection.fetchval(query)


async def patch_project(connection: Connection, pk: int, data: Dict[str, Any]) -> Dict[str, Any]:
    query = (
        sa.update(projects)
        .where(projects.c.id == pk)
        .values(**data)
    )
    await connection.fetch(query)

    return data


async def delete_project(connection: Connection, pk: int) -> None:
    await connection.execute(projects.delete().where(projects.c.id == pk))
