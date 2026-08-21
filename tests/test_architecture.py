import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from models import BlocoDeNotas, db, Estudante, Pet, Tribo
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


def test_create_app_keeps_existing_user_accounts():
    from app import create_app

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        cadastrar_estudante("persist@example.com", "123456")
        db.session.commit()

    new_app = create_app()

    with new_app.app_context():
        assert autenticar_estudante("persist@example.com", "123456") is not None


def test_bloco_de_notas_persiste_por_estudante():
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        estudante = cadastrar_estudante("notas@example.com", "123456")
        nota = BlocoDeNotas.obter_ou_criar(estudante.id)
        nota.editar_anotacao("Revisar equações")
        nota.definir_hotkey("CTRL+SHIFT+N")
        db.session.commit()

        nota_recarregada = BlocoDeNotas.buscar_por_estudante(estudante.id)
        assert nota_recarregada.conteudo == "Revisar equações"
        assert nota_recarregada.hotkey == "CTRL+SHIFT+N"
        assert BlocoDeNotas.obter_ou_criar(estudante.id).id == nota.id


def test_agenda_conclui_atividade_e_nao_duplica_xp():
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        estudante = cadastrar_estudante("agenda@example.com", "123456")
        pet = Pet(nome="AgendaPet", estudante_id=estudante.id)
        db.session.add(pet)
        estudante.pet_equipado = pet
        db.session.commit()

        cliente = app.test_client()
        cliente.post("/login", data={"email": "agenda@example.com", "senha": "123456"})
        resposta = cliente.post("/api/agenda", json={
            "data": "2026-08-25",
            "titulo": "Revisar álgebra",
            "duracao_minutos": 40,
        })
        estudo_id = resposta.json["atividade"]["id"]

        resposta = cliente.post(f"/api/agenda/{estudo_id}/concluir")
        assert resposta.json["xp_ganho"] == 60
        assert pet.xp_atual == 60

        resposta = cliente.post(f"/api/agenda/{estudo_id}/concluir")
        assert resposta.json["xp_ganho"] == 0
        assert pet.xp_atual == 60
