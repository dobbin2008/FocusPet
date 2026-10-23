from flask import Blueprint, jsonify, redirect, request, session, url_for

from backend.controllers.auth_controller import login_required, pagina_estatica
from backend.services.agenda_service import (
    ConcluirAtividadeService,
    ConfirmarLembreteEnviadoService,
    CriarAtividadeService,
    EditarAtividadeService,
    ExcluirAtividadeService,
    ListarLembretesVencidosService,
    ListarAtividadesService,
)

agenda_bp = Blueprint("agenda", __name__)


class AgendaController:
    def __init__(
        self, criar_service=None, listar_service=None, concluir_service=None,
        listar_lembretes_service=None, confirmar_lembrete_service=None,
        editar_service=None, excluir_service=None,
    ):
        self.criar_service = criar_service or CriarAtividadeService()
        self.listar_service = listar_service or ListarAtividadesService()
        self.concluir_service = concluir_service or ConcluirAtividadeService()
        self.listar_lembretes_service = (
            listar_lembretes_service or ListarLembretesVencidosService()
        )
        self.confirmar_lembrete_service = (
            confirmar_lembrete_service or ConfirmarLembreteEnviadoService()
        )
        self.editar_service = editar_service or EditarAtividadeService()
        self.excluir_service = excluir_service or ExcluirAtividadeService()

    @login_required
    def agenda_page(self):
        return pagina_estatica("agenda.html")

    @login_required
    def api_agenda(self):
        try:
            if request.method == "POST":
                dados = request.get_json(silent=True)
                if not isinstance(dados, dict):
                    return jsonify({"erro": "Informe os dados da atividade em formato JSON."}), 400
                atividade = self.criar_service.execute(session["user_id"], dados)
                return jsonify({"sucesso": True, "atividade": atividade}), 201
            return jsonify({"sucesso": True, "atividades": self.listar_service.execute(session["user_id"])}), 200
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

    @login_required
    def concluir_estudo(self, estudo_id):
        try:
            return jsonify(self.concluir_service.execute(session["user_id"], estudo_id)), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def editar_estudo(self, estudo_id):
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            return jsonify({"erro": "Informe os dados da atividade em formato JSON."}), 400
        try:
            atividade = self.editar_service.execute(
                session["user_id"], estudo_id, dados
            )
            return jsonify({"sucesso": True, "atividade": atividade}), 200
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def excluir_estudo(self, estudo_id):
        try:
            return jsonify(
                self.excluir_service.execute(session["user_id"], estudo_id)
            ), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def lembretes_vencidos(self):
        return jsonify({
            "sucesso": True,
            "lembretes": self.listar_lembretes_service.execute(session["user_id"]),
        })

    @login_required
    def confirmar_lembrete(self, estudo_id):
        confirmado = self.confirmar_lembrete_service.execute(
            session["user_id"], estudo_id
        )
        if not confirmado:
            return jsonify({"erro": "Lembrete não encontrado ou já enviado."}), 404
        return jsonify({"sucesso": True})


agenda_controller = AgendaController()
agenda_bp.add_url_rule("/agenda", view_func=agenda_controller.agenda_page, methods=["GET"])
agenda_bp.add_url_rule("/api/agenda", view_func=agenda_controller.api_agenda, methods=["GET", "POST"])
agenda_bp.add_url_rule(
    "/api/agenda/lembretes-vencidos",
    view_func=agenda_controller.lembretes_vencidos,
    methods=["GET"],
)
agenda_bp.add_url_rule(
    "/api/agenda/<int:estudo_id>/lembrete-enviado",
    view_func=agenda_controller.confirmar_lembrete,
    methods=["POST"],
)
agenda_bp.add_url_rule("/api/agenda/<int:estudo_id>/concluir", view_func=agenda_controller.concluir_estudo, methods=["POST"])
agenda_bp.add_url_rule("/api/agenda/<int:estudo_id>", view_func=agenda_controller.editar_estudo, methods=["PATCH"])
agenda_bp.add_url_rule("/api/agenda/<int:estudo_id>", view_func=agenda_controller.excluir_estudo, methods=["DELETE"])