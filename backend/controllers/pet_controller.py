from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import developer_required, login_required
from backend.services.pet_service import (
    ConcederXpTestePetService,
    CriarPetsIniciaisService,
    EquiparPetService,
    ListarPetsDisponiveisService,
    serializar_pet,
)

pet_bp = Blueprint("pet", __name__)


class PetController:
    def __init__(self, listar_service=None, equipar_service=None, iniciais_service=None, xp_teste_service=None):
        self.listar = listar_service or ListarPetsDisponiveisService()
        self.equipar = equipar_service or EquiparPetService()
        self.iniciais = iniciais_service or CriarPetsIniciaisService()
        self.xp_teste = xp_teste_service or ConcederXpTestePetService()

    @login_required
    def criar_pets_iniciais(self):
        pets = self.iniciais.execute(session["user_id"])
        return jsonify({"sucesso": True, "pets": [serializar_pet(pet) for pet in pets]})

    @login_required
    def listar_pets(self):
        return jsonify({"pets": [
            serializar_pet(pet)
            for pet in self.listar.execute(session["user_id"])
        ]})

    @login_required
    def equipar_pet(self):
        dados = request.get_json(silent=True) or {}
        try:
            pet = self.equipar.execute(session["user_id"], dados.get("pet_id"))
            return jsonify({"sucesso": True, "pet": serializar_pet(pet)})
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @developer_required
    def conceder_xp_teste(self):
        try:
            pet = self.xp_teste.execute(session["user_id"])
            return jsonify({
                "sucesso": True,
                "xp_ganho": self.xp_teste.XP_DE_TESTE,
                "pet": serializar_pet(pet),
            })
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404


pet_controller = PetController()
pet_bp.add_url_rule("/api/pets/iniciais", view_func=pet_controller.criar_pets_iniciais, methods=["POST"])
pet_bp.add_url_rule("/api/pets", view_func=pet_controller.listar_pets, methods=["GET"])
pet_bp.add_url_rule("/api/pets/equipar", view_func=pet_controller.equipar_pet, methods=["POST"])
pet_bp.add_url_rule("/api/pets/teste/ganhar-xp", view_func=pet_controller.conceder_xp_teste, methods=["POST"])