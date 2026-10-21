from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import login_required, pagina_estatica
from backend.services.materias_service import (
    CadastrarMateriaService,
    EditarMateriaService,
    ListarMateriasService,
)

materias_bp = Blueprint("materias", __name__)


class MateriasController:
    def __init__(self, services=None):
        services = services or {}
        self.listar = services.get("listar", ListarMateriasService())
        self.cadastrar = services.get("cadastrar", CadastrarMateriaService())
        self.editar = services.get("editar", EditarMateriaService())

    @login_required
    def pagina(self):
        return pagina_estatica("materias.html")

    @login_required
    def listar_ou_cadastrar(self):
        estudante_id = session["user_id"]
        dados = request.get_json(silent=True)
        if request.method == "POST" and not isinstance(dados, dict):
            return jsonify({"erro": "Informe os dados da matéria em formato JSON."}), 400
        try:
            if request.method == "POST":
                materia = self.cadastrar.execute(
                    estudante_id, dados
                )
                return jsonify({"sucesso": True, "materia": materia}), 201
            return jsonify({
                "sucesso": True,
                "materias": self.listar.execute(estudante_id),
            })
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

    @login_required
    def editar_materia(self, materia_id):
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            return jsonify({"erro": "Informe os dados da matéria em formato JSON."}), 400
        try:
            materia = self.editar.execute(
                session["user_id"],
                materia_id,
                dados,
            )
            return jsonify({"sucesso": True, "materia": materia})
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404


materias_controller = MateriasController()
materias_bp.add_url_rule(
    "/materias", view_func=materias_controller.pagina, methods=["GET"]
)
materias_bp.add_url_rule(
    "/api/materias",
    view_func=materias_controller.listar_ou_cadastrar,
    methods=["GET", "POST"],
)
materias_bp.add_url_rule(
    "/api/materias/<int:materia_id>",
    view_func=materias_controller.editar_materia,
    methods=["PATCH"],
)
