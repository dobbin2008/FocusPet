from flask import Blueprint, redirect, render_template, request, url_for

from services.admin_service import (
    criar_pet,
    criar_tribo,
    deletar_pet,
    deletar_tribo,
    listar_pets,
    listar_tribos,
)
from services.auth_service import cadastrar_estudante, listar_estudantes
from .auth_controller import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


class AdminController:
    @login_required
    def painel_admin(self):
        if request.method == "POST":
            action = request.form.get("action")
            try:
                if action == "criar_estudante":
                    cadastrar_estudante(request.form.get("email", "").strip(), request.form.get("senha", ""))
                elif action == "criar_pet":
                    nome = request.form.get("nome", "").strip()
                    if nome:
                        criar_pet(nome)
                elif action == "criar_tribo":
                    materia = request.form.get("materia", "").strip()
                    if materia:
                        criar_tribo(materia)
            except ValueError:
                pass

        return render_template(
            "admin.html",
            estudantes=listar_estudantes(),
            pets=listar_pets(),
            tribos=listar_tribos(),
        )

    @login_required
    def deletar_pet_admin(self, pet_id):
        deletar_pet(pet_id)
        return redirect(url_for("admin.painel_admin"))

    @login_required
    def deletar_tribo_admin(self, tribo_id):
        deletar_tribo(tribo_id)
        return redirect(url_for("admin.painel_admin"))


admin_controller = AdminController()
admin_bp.add_url_rule("/", view_func=admin_controller.painel_admin, methods=["GET", "POST"])
admin_bp.add_url_rule("/pets/<int:pet_id>/delete", view_func=admin_controller.deletar_pet_admin, methods=["POST"])
admin_bp.add_url_rule("/tribos/<int:tribo_id>/delete", view_func=admin_controller.deletar_tribo_admin, methods=["POST"])
