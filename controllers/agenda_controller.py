from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from services.agenda_service import AgendaService

agenda_bp = Blueprint("agenda", __name__, url_prefix="")


class AgendaController:
    def __init__(self, service):
        self.service = service

    def agenda_page(self):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("agenda.html")

    def api_agenda(self):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            if request.method == "POST":
                atividade = self.service.criar(session["user_id"], request.get_json(silent=True) or {})
                return jsonify({"sucesso": True, "atividade": atividade}), 201
            return jsonify({"sucesso": True, "atividades": self.service.listar(session["user_id"])}), 200
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500

    def concluir_estudo(self, estudo_id):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            return jsonify(self.service.concluir(session["user_id"], estudo_id)), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404


agenda_controller = AgendaController(AgendaService())
agenda_bp.add_url_rule("/agenda", view_func=agenda_controller.agenda_page)
agenda_bp.add_url_rule("/api/agenda", view_func=agenda_controller.api_agenda, methods=["GET", "POST"])
agenda_bp.add_url_rule("/api/agenda/<int:estudo_id>/concluir", view_func=agenda_controller.concluir_estudo, methods=["POST"])