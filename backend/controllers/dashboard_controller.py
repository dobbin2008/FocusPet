from flask import Blueprint, jsonify, session

from backend.controllers.auth_controller import login_required
from backend.services.dashboard_service import ObterDashboardService

dashboard_bp = Blueprint("dashboard", __name__)


class DashboardController:
    def __init__(self, service=None):
        self.service = service or ObterDashboardService()

    @login_required
    def obter(self):
        try:
            return jsonify(self.service.execute(session["user_id"]))
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404


dashboard_controller = DashboardController()
dashboard_bp.add_url_rule("/api/dashboard", view_func=dashboard_controller.obter, methods=["GET"])