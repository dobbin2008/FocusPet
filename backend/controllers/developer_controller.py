from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import developer_required
from backend.services.developer_service import SimularEstudoService

developer_bp = Blueprint("developer", __name__)


class DeveloperController:
    def __init__(self, simular_estudo_service=None):
        self.simular_estudo = simular_estudo_service or SimularEstudoService()

    @developer_required
    def simular_estudo_concluido(self):
        dados = request.get_json(silent=True) or {}
        try:
            resultado = self.simular_estudo.execute(
                session["user_id"], dados.get("horas")
            )
            return jsonify(resultado), 201
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400


developer_controller = DeveloperController()
developer_bp.add_url_rule(
    "/api/desenvolvedor/simular-estudo",
    view_func=developer_controller.simular_estudo_concluido,
    methods=["POST"],
)
