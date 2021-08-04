from server.apps.dashboard.routes import routes as dashboard_routes
from server.apps.management.routes import routes as management_routes
from server.apps.projects.routes import routes as projects_routes


routes = dashboard_routes + projects_routes + management_routes


__all__ = ['routes']
