from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.sql import func, select
from asyncpg import Connection
from db.utils import from_record_to_dict

import settings
from db.tables import metadata


logs = sa.Table(
    'logs',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('remote_addr', sa.String, nullable=True),
    sa.Column('remote_user', sa.String, nullable=True),
    sa.Column('time_local', sa.DateTime, nullable=True),
    sa.Column('request', sa.String, nullable=True),
    sa.Column('status', sa.SmallInteger, nullable=True),
    sa.Column('body_bytes_sent', sa.Integer, nullable=True),
    sa.Column('http_referer', sa.String, nullable=True),
    sa.Column('http_user_agent', sa.String, nullable=True),
    sa.Column(
        'created_at', sa.DateTime, nullable=False, server_default=func.now()
    ),
    sa.Column('project_id', sa.ForeignKey(
        'projects.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False
    ),
)


async def get_logs_by_project_id(connection: Connection, project_id: int):
    query = (
        select(
            [
                logs.c.id,
                logs.c.remote_addr,
                logs.c.remote_user,
                sa.cast(logs.c.time_local, sa.String).label('time_local'),
                logs.c.request,
                logs.c.status,
                logs.c.body_bytes_sent,
                logs.c.http_referer,
                logs.c.http_user_agent,
                sa.cast(logs.c.created_at, sa.String).label('created_at'),
                logs.c.project_id,
            ]
        )
        .where(logs.c.project_id == project_id)
        .order_by(logs.c.created_at)
        .limit(100)
    )
    data = await connection.fetch(query)

    return from_record_to_dict(data)


async def analyze_logs(connection: Connection, project_id: int, **kwargs):
    template = settings.sql_templates.get_template('analyze_logs.tpl')

    sql = template.render(
        pid=project_id,
        from_=kwargs.get(
            'from', datetime(1970, 1, 1).strftime('%Y-%m-%d')
        ),
        to_=kwargs.get(
            'to', datetime(2030, 2, 2).strftime('%Y-%m-%d')
        )
    )

    result = [dict(record) for record in (await connection.fetch(sql))]

    return {
        'total_requests': sum(record['total_requests'] for record in result),
        'unique_users': sum(record['unique_users'] for record in result),
        'referrers': sum(record['referrers'] for record in result),
        'grouped_by_statuses': result,
        'total_bytes_sent': sum(
            record['total_bytes_sent'] for record in result
        ),
    }
