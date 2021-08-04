import os
import yaml
import logging
import copy as cp

import click
import psycopg2
from aiohttp import web
from alembic import command
from alembic.config import Config

from server.app import init_application


def get_postgresql_url():
    url = os.getenv('POSTGRESQL_URL')

    if not url:
        raise ValueError('Setup POSTGRESQL_URL environment variable')

    return url


@click.command('migrate')
def migrate():
    url = get_postgresql_url()

    cfg = Config(file_='db/migrations/alembic.ini')
    cfg.set_main_option('script_location', 'db/migrations/')
    cfg.set_main_option('sqlalchemy.url', url)

    click.echo(
        f'Start to initialize your '
        f'database with your database url: {url}'
    )

    command.upgrade(cfg, 'heads')


@click.command('makemigrations')
def makemigrations():
    url = get_postgresql_url()

    cfg = Config(file_='db/migrations/alembic.ini')
    cfg.set_main_option('script_location', 'db/migrations/')
    cfg.set_main_option('sqlalchemy.url', url)

    click.echo(
        f'Make migrations in your '
        f'database with url: {url}'
    )

    command.revision(cfg, autogenerate=True)


@click.command('runserver')
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8000)
@click.option('--config')
@click.option('--start_streams', type=bool, default=False)
@click.option('--logging_level', default='INFO')
def runserver(host, port, config, start_streams, logging_level):
    params_ = cp.copy(locals())

    if not config:
        raise ValueError('Config is not specified.')

    with open(config) as file:
        config = yaml.load(file, yaml.FullLoader)

    app = init_application(config)
    app['params'] = params_
    logging.basicConfig(
        level=getattr(logging, logging_level)
    )
    web.run_app(app, host=host, port=port)


@click.command('clean')
def clean():
    connection = psycopg2.connect(
        dsn=get_postgresql_url()
    )

    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT table_name '
            'FROM information_schema.tables '
            'WHERE table_schema = \'public\' '
        )

        tables = [t[0] for t in cursor.fetchall()]

        for table in tables:
            if table != 'alembic_version':
                cursor.execute(
                    f'TRUNCATE {table} CASCADE'
                )

    connection.commit()


@click.group()
def cli():
    pass


cli.add_command(migrate)
cli.add_command(makemigrations)
cli.add_command(runserver)
cli.add_command(clean)


if __name__ == '__main__':
    cli()
