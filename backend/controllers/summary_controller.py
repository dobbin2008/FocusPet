from flask import Blueprint, jsonify, session

from backend.controllers.auth_controller import login_required, pagina_estatica
from backend.services.summary_service import GerarResumoSemanalService

summary_bp = Blueprint("summary", __name__)


class SummaryController:
    def __init__(self, service=None):
        self.service = service or GerarResumoSemanalService()

    @login_required
    def gerar(self):
        try:
            return jsonify(self.service.execute(session["user_id"]))
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def pagina(self):
        return pagina_estatica("resumo.html")


summary_controller = SummaryController()
summary_bp.add_url_rule("/api/resumo-semanal", view_func=summary_controller.gerar, methods=["GET"])
summary_bp.add_url_rule("/resumo", view_func=summary_controller.pagina, methods=["GET"])