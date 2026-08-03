import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from models import db, Estudante, Pet, Tribo
from services.auth_service import cadastrar_estudante, autenticar_estudante
from services.admin_service import criar_pet, criar_tribo, listar_pets, listar_tribos


def test_service_uses_model_crud_methods():
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        estudante = cadastrar_estudante("teste@example.com", "123456")
        assert estudante.id is not None
        assert autenticar_estudante("teste@example.com", "123456") is not None

        pet = criar_pet("Fofinho")
        assert pet.id is not None
        assert len(listar_pets()) == 1

        tribo = criar_tribo("Matemática")
        assert tribo.id is not None
        assert len(listar_tribos()) == 1
