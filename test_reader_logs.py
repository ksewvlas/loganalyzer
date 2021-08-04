if __name__ == '__main__':
    from db import create_alchemy_engine
    from streaming.queries import add_log
    from streaming import NginxLogsParser

    with open('nginx_logs/access.log') as log_file:
        data = log_file.readlines()

    parser = NginxLogsParser()

    connection = create_alchemy_engine(
        {
            'host': 'localhost',
            'port': 5430,
            'user': 'test',
            'password': 'test',
            'db': 'test',
        }
    )

    for line in data:
        add_log(connection, 56, parser.parse(line))
