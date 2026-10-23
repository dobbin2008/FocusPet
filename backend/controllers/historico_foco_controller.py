from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import login_required, pagina_estatica
from backend.services.historico_foco_service import (
    ConsultarDetalheSessaoFocoService,
    ListarHistoricoFocoService,
)

historico_foco_bp = Blueprint("historico_foco", __name__)


class HistoricoFocoController:
    def __init__(self, listar_service=None, detalhe_service=None):
        self.listar_service = listar_service or ListarHistoricoFocoService()
        self.detalhe_service = (
            detalhe_service or ConsultarDetalheSessaoFocoService()
        )

    @login_required
    def pagina(self):
        return pagina_estatica("historico_foco.html")

    @login_required
    def listar(self):
        try:
            sessoes = self.listar_service.execute(
                session["user_id"],
                request.args.get("inicio"),
                request.args.get("fim"),
            )
            return jsonify({"sucesso": True, "sessoes": sessoes})
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

    @login_required
    def detalhe(self, sessao_id):
        try:
            sessao = self.detalhe_service.execute(session["user_id"], sessao_id)
            return jsonify({"sucesso": True, "sessao": sessao})
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404


historico_foco_controller = HistoricoFocoController()
historico_foco_bp.add_url_rule(
    "/historico-foco", view_func=historico_foco_controller.pagina, methods=["GET"]
)
historico_foco_bp.add_url_rule(
    "/api/foco/historico", view_func=historico_foco_controller.listar, methods=["GET"]
)
historico_foco_bp.add_url_rule(
    "/api/foco/historico/<int:sessao_id>",
    view_func=historico_foco_controller.detalhe,
    methods=["GET"],
)
