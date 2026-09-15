import os

from flask import Blueprint, jsonify, redirect, request, send_from_directory, session, url_for

from services.agenda_service import (
    ConcluirAtividadeService,
    CriarAtividadeService,
    ListarAtividadesService,
)

agenda_bp = Blueprint("agenda", __name__, url_prefix="")


def pagina_estatica(nome):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"), nome)


class AgendaController:
    def __init__(self, criar_service=None, listar_service=None, concluir_service=None):
        self.criar_service = criar_service or CriarAtividadeService()
        self.listar_service = listar_service or ListarAtividadesService()
        self.concluir_service = concluir_service or ConcluirAtividadeService()

    def agenda_page(self):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return pagina_estatica("agenda.html")

    def api_agenda(self):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            if request.method == "POST":
                atividade = self.criar_service.execute(session["user_id"], request.get_json(silent=True) or {})
                return jsonify({"sucesso": True, "atividade": atividade}), 201
            return jsonify({"sucesso": True, "atividades": self.listar_service.execute(session["user_id"])}), 200
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500

    def concluir_estudo(self, estudo_id):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            return jsonify(self.concluir_service.execute(session["user_id"], estudo_id)), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404


agenda_controller = AgendaController()
agenda_bp.add_url_rule("/agenda", view_func=agenda_controller.agenda_page)
agenda_bp.add_url_rule("/api/agenda", view_func=agenda_controller.api_agenda, methods=["GET", "POST"])
agenda_bp.add_url_rule("/api/agenda/<int:estudo_id>/concluir", view_func=agenda_controller.concluir_estudo, methods=["POST"])