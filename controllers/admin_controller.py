import os

from flask import Blueprint, jsonify, redirect, request, send_from_directory, url_for

from services.admin_service import (
    CriarPetService,
    CriarTriboService,
    DeletarPetService,
    DeletarTriboService,
    ListarPetsService,
    ListarTribosService,
)
from services.auth_service import CadastrarEstudanteService, ListarEstudantesService
from .auth_controller import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def pagina_estatica(nome):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"), nome)


class AdminController:
    def __init__(self, services=None):
        services = services or {}
        self.cadastrar_estudante = services.get("cadastrar_estudante", CadastrarEstudanteService())
        self.criar_pet = services.get("criar_pet", CriarPetService())
        self.criar_tribo = services.get("criar_tribo", CriarTriboService())
        self.listar_estudantes = services.get("listar_estudantes", ListarEstudantesService())
        self.listar_pets = services.get("listar_pets", ListarPetsService())
        self.listar_tribos = services.get("listar_tribos", ListarTribosService())
        self.deletar_pet = services.get("deletar_pet", DeletarPetService())
        self.deletar_tribo = services.get("deletar_tribo", DeletarTriboService())

    @login_required
    def painel_admin(self):
        if request.method == "POST":
            action = request.form.get("action")
            try:
                if action == "criar_estudante":
                    self.cadastrar_estudante.execute(request.form.get("email", "").strip(), request.form.get("senha", ""))
                elif action == "criar_pet":
                    nome = request.form.get("nome", "").strip()
                    if nome:
                        self.criar_pet.execute(nome)
                elif action == "criar_tribo":
                    materia = request.form.get("materia", "").strip()
                    if materia:
                        self.criar_tribo.execute(materia)
            except ValueError:
                pass

        return pagina_estatica("admin.html")

    @login_required
    def dados_admin(self):
        return jsonify({
            "estudantes": [{"id": estudante.id, "email": estudante.email} for estudante in self.listar_estudantes.execute()],
            "pets": [{"id": pet.id, "nome": pet.nome, "nivel": pet.nivel} for pet in self.listar_pets.execute()],
            "tribos": [{"id": tribo.id, "materia": tribo.materia} for tribo in self.listar_tribos.execute()],
        })

    @login_required
    def deletar_pet_admin(self, pet_id):
        self.deletar_pet.execute(pet_id)
        return redirect(url_for("admin.painel_admin"))

    @login_required
    def deletar_tribo_admin(self, tribo_id):
        self.deletar_tribo.execute(tribo_id)
        return redirect(url_for("admin.painel_admin"))


admin_controller = AdminController()
admin_bp.add_url_rule("/", view_func=admin_controller.painel_admin, methods=["GET", "POST"])
admin_bp.add_url_rule("/api/dados", view_func=admin_controller.dados_admin, methods=["GET"])
admin_bp.add_url_rule("/pets/<int:pet_id>/delete", view_func=admin_controller.deletar_pet_admin, methods=["POST"])
admin_bp.add_url_rule("/tribos/<int:tribo_id>/delete", view_func=admin_controller.deletar_tribo_admin, methods=["POST"])
