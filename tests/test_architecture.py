import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import obter_banco
from services.admin_service import CriarPetService, CriarTriboService, ListarPetsService, ListarTribosService
from services.auth_service import AutenticarEstudanteService, CadastrarEstudanteService


def limpar_dados():
    banco = obter_banco()
    banco.execute("UPDATE estudantes SET pet_equipado_id = NULL, tribo_id = NULL")
    banco.execute("UPDATE pets SET estudante_id = NULL, tribo_id = NULL")
    banco.execute("DELETE FROM estudos")
    banco.execute("DELETE FROM agendas")
    banco.execute("DELETE FROM blocos_de_notas")
    banco.execute("DELETE FROM sessoes_de_foco")
    banco.execute("DELETE FROM listas_bloqueadas")
    banco.execute("DELETE FROM pets")
    banco.execute("DELETE FROM tribos")
    banco.execute("DELETE FROM estudantes")
    banco.commit()


def test_sqlite_services_crud():
    with app.app_context():
        limpar_dados()
        estudante = CadastrarEstudanteService().execute("teste@example.com", "123456")
        assert estudante.id is not None
        assert AutenticarEstudanteService().execute("teste@example.com", "123456").id == estudante.id
        assert CriarPetService().execute("Fofinho").id is not None
        assert len(ListarPetsService().execute()) == 1
        assert CriarTriboService().execute("Matemática").id is not None
        assert len(ListarTribosService().execute()) == 1


def test_notas_persistem_por_estudante():
    with app.app_context():
        limpar_dados()
        estudante = CadastrarEstudanteService().execute("notas@example.com", "123456")
        cliente = app.test_client()
        cliente.post("/login", data={"email": estudante.email, "senha": "123456"})
        resposta = cliente.put("/api/notas", json={"conteudo": "Revisar equações", "hotkey": "CTRL+SHIFT+N"})
        assert resposta.status_code == 200
        resposta = cliente.get("/api/notas")
        assert resposta.json["conteudo"] == "Revisar equações"
        assert resposta.json["hotkey"] == "CTRL+SHIFT+N"


def test_agenda_conclui_atividade_e_nao_duplica_xp():
    with app.app_context():
        limpar_dados()
        estudante = CadastrarEstudanteService().execute("agenda@example.com", "123456")
        pet = CriarPetService().execute("AgendaPet")
        obter_banco().execute("UPDATE pets SET estudante_id = ?, xp_atual = 0 WHERE id = ?", (estudante.id, pet.id))
        obter_banco().execute("UPDATE estudantes SET pet_equipado_id = ? WHERE id = ?", (pet.id, estudante.id))
        obter_banco().commit()
        cliente = app.test_client()
        cliente.post("/login", data={"email": estudante.email, "senha": "123456"})
        resposta = cliente.post("/api/agenda", json={"data": "2026-08-25", "titulo": "Revisar álgebra", "duracao_minutos": 40})
        estudo_id = resposta.json["atividade"]["id"]
        resposta = cliente.post(f"/api/agenda/{estudo_id}/concluir")
        assert resposta.json["xp_ganho"] == 60
        resposta = cliente.post(f"/api/agenda/{estudo_id}/concluir")
        assert resposta.json["xp_ganho"] == 0


def test_api_admin_exige_login_e_retorna_dados():
    with app.app_context():
        limpar_dados()
        cliente = app.test_client()
        assert cliente.get("/admin/api/dados").status_code == 302
        estudante = CadastrarEstudanteService().execute("admin@example.com", "123456")
        cliente.post("/login", data={"email": estudante.email, "senha": "123456", "next": "admin"})
        resposta = cliente.get("/admin/api/dados")
        assert resposta.status_code == 200
        assert "estudantes" in resposta.json
