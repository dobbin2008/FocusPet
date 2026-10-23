from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import login_required
from backend.services.notas_service import (
    AtualizarAtalhoNotaService,
    AtualizarNotaService,
    CriarNotaService,
    ExcluirNotaService,
    ListarNotasService,
    ObterAtalhoNotaService,
    ObterNotaService,
    SalvarNotaLegadaService,
)

notas_bp = Blueprint("notas", __name__)


class NotasController:
    def __init__(self, services=None):
        services = services or {}
        self.listar = services.get("listar", ListarNotasService())
        self.criar = services.get("criar", CriarNotaService())
        self.obter = services.get("obter", ObterNotaService())
        self.atualizar = services.get("atualizar", AtualizarNotaService())
        self.excluir = services.get("excluir", ExcluirNotaService())
        self.obter_atalho = services.get("obter_atalho", ObterAtalhoNotaService())
        self.atualizar_atalho = services.get("atualizar_atalho", AtualizarAtalhoNotaService())
        self.salvar_legada = services.get("salvar_legada", SalvarNotaLegadaService())

    @login_required
    def notas(self):
        estudante_id = session["user_id"]
        try:
            dados = request.get_json(silent=True) or {}
            if request.method == "POST":
                return jsonify({"sucesso": True, "nota": self.criar.execute(estudante_id, dados)}), 201
            if request.method == "PUT":
                retorno = {"sucesso": True}
                if "hotkey" in dados:
                    retorno["hotkey"] = self.atualizar_atalho.execute(estudante_id, dados["hotkey"])
                if "conteudo" in dados:
                    nota = self.salvar_legada.execute(estudante_id, dados["conteudo"])
                    retorno.update({"nota": nota, "conteudo": nota["conteudo"]})
                if len(retorno) == 1:
                    raise ValueError("Informe o conteúdo da nota ou o atalho.")
                return jsonify(retorno)
            if request.method == "DELETE":
                notas = self.listar.execute(estudante_id)
                if notas:
                    self.excluir.execute(estudante_id, notas[0]["id"])
                return jsonify({"sucesso": True})
            notas = self.listar.execute(estudante_id)
            hotkey = self.obter_atalho.execute(estudante_id)
            return jsonify({
                "sucesso": True,
                "notas": notas,
                "conteudo": notas[0]["conteudo"] if notas else "",
                "hotkey": hotkey,
            })
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def nota(self, nota_id):
        estudante_id = session["user_id"]
        try:
            if request.method == "GET":
                return jsonify({"sucesso": True, "nota": self.obter.execute(estudante_id, nota_id)})
            if request.method == "PUT":
                nota = self.atualizar.execute(
                    estudante_id, nota_id, request.get_json(silent=True) or {}
                )
                return jsonify({"sucesso": True, "nota": nota})
            self.excluir.execute(estudante_id, nota_id)
            return jsonify({"sucesso": True})
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def atalho(self):
        estudante_id = session["user_id"]
        try:
            if request.method == "PUT":
                hotkey = self.atualizar_atalho.execute(
                    estudante_id, (request.get_json(silent=True) or {}).get("hotkey")
                )
            else:
                hotkey = self.obter_atalho.execute(estudante_id)
            return jsonify({"sucesso": True, "hotkey": hotkey})
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400


notas_controller = NotasController()
notas_bp.add_url_rule("/api/notas", view_func=notas_controller.notas, methods=["GET", "POST", "PUT", "DELETE"])
notas_bp.add_url_rule("/api/notas/<int:nota_id>", view_func=notas_controller.nota, methods=["GET", "PUT", "DELETE"])
notas_bp.add_url_rule("/api/notas/atalho", view_func=notas_controller.atalho, methods=["GET", "PUT"])