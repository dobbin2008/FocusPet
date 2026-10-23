from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import login_required, pagina_estatica
from backend.services.metas_service import (
    ConfigurarMetasEstudoService,
    ObterMetasEstudoService,
)

metas_bp = Blueprint("metas", __name__)


class MetasController:
    def __init__(self, obter_service=None, configurar_service=None):
        self.obter_service = obter_service or ObterMetasEstudoService()
        self.configurar_service = (
            configurar_service or ConfigurarMetasEstudoService()
        )

    @login_required
    def pagina(self):
        return pagina_estatica("metas.html")

    @login_required
    def api_metas(self):
        estudante_id = session["user_id"]
        if request.method == "GET":
            return jsonify(self.obter_service.execute(estudante_id))
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            return jsonify({"erro": "Envie as metas em formato JSON."}), 400
        try:
            return jsonify(self.configurar_service.execute(estudante_id, dados))
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400


metas_controller = MetasController()
metas_bp.add_url_rule(
    "/metas", view_func=metas_controller.pagina, methods=["GET"]
)
metas_bp.add_url_rule(
    "/api/metas", view_func=metas_controller.api_metas, methods=["GET", "PUT"]
)
