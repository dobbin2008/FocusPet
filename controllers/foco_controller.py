from flask import Blueprint, jsonify, session

from services.foco_service import (
    ConsultarSessaoFocoService,
    EncerrarModoFocoService,
    IniciarModoFocoService,
    RegistrarDistracaoService,
)

foco_bp = Blueprint("foco", __name__, url_prefix="")


class FocoController:
    def __init__(self, services=None):
        services = services or {}
        self.iniciar = services.get("iniciar", IniciarModoFocoService())
        self.encerrar = services.get("encerrar", EncerrarModoFocoService())
        self.consultar = services.get("consultar", ConsultarSessaoFocoService())
        self.distracao = services.get("distracao", RegistrarDistracaoService())

    def iniciar_modo_foco(self):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            sessao = self.iniciar.execute(session["user_id"])
            return jsonify({"sucesso": True, "sessao_id": sessao.id, "mensagem": "Modo foco iniciado!"}), 200
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500

    def encerrar_modo_foco(self, sessao_id):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            sessao = self.encerrar.execute(session["user_id"], sessao_id)
            return jsonify({
                "sucesso": True,
                "tempo_minutos": sessao.tempo_total_minutos,
                "vezes_distraido": sessao.vezes_distraido,
                "xp_ganho": sessao.xp_ganho,
                "mensagem": f"Sessão finalizada! Você ganhou {sessao.xp_ganho} XP",
            }), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500

    def obter_status_sessao(self, sessao_id):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            sessao = self.consultar.execute(session["user_id"], sessao_id)
            return jsonify({
                "sucesso": True,
                "sessao_id": sessao.id,
                "modo_ativo": sessao.modo_ativo,
                "tempo_total_minutos": sessao.tempo_total_minutos,
                "vezes_distraido": sessao.vezes_distraido,
                "inicio": sessao.inicio,
                "fim": sessao.fim,
                "xp_ganho": sessao.xp_ganho,
            }), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    def registrar_distracao(self, sessao_id):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            sessao = self.distracao.execute(session["user_id"], sessao_id)
            return jsonify({"sucesso": True, "vezes_distraido": sessao.vezes_distraido}), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500


foco_controller = FocoController()
foco_bp.add_url_rule("/api/foco/iniciar", view_func=foco_controller.iniciar_modo_foco, methods=["POST"])
foco_bp.add_url_rule("/api/foco/encerrar/<int:sessao_id>", view_func=foco_controller.encerrar_modo_foco, methods=["POST"])
foco_bp.add_url_rule("/api/foco/status/<int:sessao_id>", view_func=foco_controller.obter_status_sessao, methods=["GET"])
foco_bp.add_url_rule("/api/foco/registrar-distracao/<int:sessao_id>", view_func=foco_controller.registrar_distracao, methods=["POST"])