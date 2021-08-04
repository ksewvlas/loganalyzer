from db.tables import logs, projects


def add_log(connection, pid, log):
    with connection.begin():
        try:
            connection.execute(
                logs.insert().values(project_id=pid, **log)
            )
        except TypeError:
            ...


def get_settings_by_pid(connection, pid):
    cursor = connection.execute(
        projects
        .select()
        .where(projects.c.id == pid)
    )
    return cursor.fetchone()['settings']
