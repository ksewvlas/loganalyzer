import os

from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sql_templates = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'loganalyzer/db/templates/')),
)

