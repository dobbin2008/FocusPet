import sqlite3
from io import BytesIO
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image
from sqlalchemy import inspect
from werkzeug.security import check_password_hash

from app import create_app
from backend.extensions import db
from backend.database import inicializar_banco
from backend.models import (
    Agenda,
    BlocoNotas,
    Estudante,
    Estudo,
    Materia,
    BonusMeta,
    MetaEstudo,
    Nota,
    Pet,
    SessaoFoco,
)
from backend.services.auth_service import validar_senha
from backend.xp import (
    calcular_xp_atividade,
    calcular_xp_bonus_meta,
    calcular_xp_foco,
)

SENHA_TESTE = "StudyBuddy123!"


@pytest.fixture
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        "PROFILE_UPLOAD_FOLDER": str(tmp_path / "profile_photos"),
        "TURNSTILE_TEST_BYPASS": True,
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.session.execute(db.update(Estudante).values(pet_equipado_id=None))
        db.session.execute(db.update(Pet).values(estudante_id=None))
        db.session.commit()
        db.drop_all()
        db.engine.dispose()


def cadastrar_e_entrar(cliente, email="estudante@example.com", senha=SENHA_TESTE):
    resposta = cliente.post("/api/auth/cadastro", json={"email": email, "senha": senha})
    assert resposta.status_code == 201
    resposta = cliente.post("/api/auth/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200


def test_senha_exige_complexidade_minima():
    validar_senha("StudyBuddy123!")
    validar_senha("Abcdefghij1#")
    validar_senha("Ábcdefghij1!")
    for senha_fraca in (
        "short1A!",
        "abcdefghijkl1!",
        "ABCDEFGHIJKL1!",
        "Abcdefghijkl!",
        "Abcdefghijkl1",
        "Abcdefghij1 ",
    ):
        with pytest.raises(ValueError):
            validar_senha(senha_fraca)


def test_dashboard_retorna_perfil_sem_ranking(app):
    cliente = app.test_client()
    resposta = cliente.post("/api/auth/cadastro", json={
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "senha": SENHA_TESTE,
    })
    assert resposta.status_code == 201
    cliente.post("/api/auth/login", json={"email": "ana@example.com", "senha": SENHA_TESTE})

    dashboard = cliente.get("/api/dashboard").json
    assert dashboard["estudante"]["nome"] == "Ana Souza"
    assert dashboard["estudante"]["iniciais"] == "AS"
    assert dashboard["estudante"]["xp_total"] == 0
    assert dashboard["estudante"]["foto_url"] is None
    assert "ranking" not in dashboard
    assert cliente.get("/api/perfil/foto").status_code == 404


def test_cadastro_recebe_nome_foto_e_servico_protege_imagem(app):
    cliente = app.test_client()
    imagem = BytesIO()
    Image.new("RGB", (800, 600), "#287c8e").save(imagem, format="PNG")
    imagem.seek(0)

    resposta = cliente.post("/api/auth/cadastro", data={
        "nome": "Rafa Focus",
        "email": "foto@example.com",
        "senha": SENHA_TESTE,
        "foto_perfil": (imagem, "perfil.png"),
    }, content_type="multipart/form-data")
    assert resposta.status_code == 201
    assert resposta.json["nome"] == "Rafa Focus"
    assert resposta.json["foto_perfil"] is True
    assert cliente.get("/api/perfil/foto").status_code == 401

    assert cliente.post("/api/auth/login", json={
        "email": "foto@example.com",
        "senha": SENHA_TESTE,
    }).status_code == 200
    dashboard = cliente.get("/api/dashboard").json
    assert dashboard["estudante"]["nome"] == "Rafa Focus"
    assert dashboard["estudante"]["iniciais"] == "RF"
    assert dashboard["estudante"]["foto_url"] == "/api/perfil/foto"

    foto = cliente.get(dashboard["estudante"]["foto_url"])
    assert foto.status_code == 200
    assert foto.mimetype == "image/webp"
    with Image.open(BytesIO(foto.data)) as imagem_salva:
        assert imagem_salva.format == "WEBP"
        assert imagem_salva.size == (512, 384)

    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "foto@example.com")
        ).scalar_one()
        assert estudante.foto_perfil
        assert Path(app.config["PROFILE_UPLOAD_FOLDER"], estudante.foto_perfil).is_file()


def test_captcha_configurado_e_cadastro_falha_fechado_quando_sem_chave(app):
    app.config.update(
        TURNSTILE_SITE_KEY="site-key-publica",
        TURNSTILE_SECRET_KEY="",
        TURNSTILE_TEST_BYPASS=False,
    )
    cliente = app.test_client()
    assert cliente.get("/api/auth/captcha-config").json == {"site_key": "site-key-publica"}
    assert b"turnstileWidget" in cliente.get("/cadastro").data

    resposta = cliente.post("/api/auth/cadastro", data={
        "nome": "Estudante",
        "email": "captcha@example.com",
        "senha": SENHA_TESTE,
        "cf-turnstile-response": "token-valido",
    })
    assert resposta.status_code == 503
    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "captcha@example.com")
        ).scalar_one_or_none()
        assert estudante is None


def test_cadastro_com_turnstile_validado_cria_conta(app, monkeypatch):
    app.config.update(
        TURNSTILE_SITE_KEY="site-key-publica",
        TURNSTILE_SECRET_KEY="secret-key-de-teste",
        TURNSTILE_TEST_BYPASS=False,
    )
    chamadas = []

    def validar_turnstile(url, *, data, timeout):
        chamadas.append((url, data, timeout))
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"success": True},
        )

    monkeypatch.setattr("backend.services.captcha_service.requests.post", validar_turnstile)
    resposta = app.test_client().post("/api/auth/cadastro", data={
        "nome": "Estudante",
        "email": "captcha-ok@example.com",
        "senha": SENHA_TESTE,
        "cf-turnstile-response": "token-de-teste",
    })
    assert resposta.status_code == 201
    assert chamadas[0][0] == "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    assert chamadas[0][1]["secret"] == "secret-key-de-teste"
    assert chamadas[0][1]["response"] == "token-de-teste"
    assert chamadas[0][2] == 8
    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "captcha-ok@example.com")
        ).scalar_one()
        assert check_password_hash(estudante.senha, SENHA_TESTE)


def test_cadastro_rejeita_foto_invalida_sem_criar_conta(app):
    cliente = app.test_client()
    resposta = cliente.post("/api/auth/cadastro", data={
        "nome": "Imagem Inválida",
        "email": "invalida@example.com",
        "senha": SENHA_TESTE,
        "foto_perfil": (BytesIO(b"isto nao e uma imagem"), "foto.png"),
    }, content_type="multipart/form-data")
    assert resposta.status_code == 400
    assert "imagem válida" in resposta.json["erro"]
    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "invalida@example.com")
        ).scalar_one_or_none()
        assert estudante is None

    grande = cliente.post("/api/auth/cadastro", data={
        "nome": "Arquivo Grande",
        "email": "grande@example.com",
        "senha": SENHA_TESTE,
        "foto_perfil": (BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "grande.png"),
    }, content_type="multipart/form-data")
    assert grande.status_code == 413
    assert grande.json["erro"] == "A imagem deve ter no máximo 5 MB"


def test_telas_e_fluxos_de_api_ate_o_banco(app):
    cliente = app.test_client()
    assert cliente.get("/login").status_code == 200
    cadastrar_e_entrar(cliente)
    assert cliente.get("/dashboard").headers["Location"] == "/"
    iniciais = cliente.post("/api/pets/iniciais")
    assert iniciais.status_code == 200
    assert [pet["linha_evolutiva"] for pet in iniciais.json["pets"]] == ["grup0", "grup1"]
    assert iniciais.json["pets"][0]["imagem_url"].endswith("weedle%20base%20grup0.png")
    assert cliente.post("/api/pets/iniciais").json["pets"] == iniciais.json["pets"]

    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "estudante@example.com")
        ).scalar_one()
        assert estudante.senha != SENHA_TESTE
        assert check_password_hash(estudante.senha, SENHA_TESTE)

    resposta = cliente.post("/api/agenda", json={
        "data": "2026-10-13",
        "titulo": "Revisar álgebra",
        "duracao_minutos": 40,
    })
    assert resposta.status_code == 201
    estudo_id = resposta.json["atividade"]["id"]
    primeira_conclusao = cliente.post(f"/api/agenda/{estudo_id}/concluir")
    segunda_conclusao = cliente.post(f"/api/agenda/{estudo_id}/concluir")
    assert primeira_conclusao.json["xp_ganho"] == 8
    assert primeira_conclusao.json["atividade"]["xp"] == 8
    assert segunda_conclusao.json["xp_ganho"] == 0
    pet_apos_agenda = cliente.get("/api/dashboard").json["pet"]
    assert pet_apos_agenda["xp_atual"] == 8
    assert pet_apos_agenda["xp_progresso_nivel"] == 8
    assert pet_apos_agenda["xp_para_proximo_nivel"] == 92

    resposta = cliente.put("/api/notas", json={"conteudo": "Revisar equações", "hotkey": "CTRL+SHIFT+N"})
    assert resposta.status_code == 200
    resposta = cliente.get("/api/notas")
    assert resposta.json["conteudo"] == "Revisar equações"
    assert resposta.json["hotkey"] == "CTRL+SHIFT+N"

    resposta = cliente.post("/api/blacklist/adicionar", json={"url": "https://example.org", "descricao": "Teste"})
    assert resposta.status_code == 201
    site_id = resposta.json["id"]
    assert cliente.delete(f"/api/blacklist/remover/{site_id}").status_code == 200
    assert cliente.get("/api/dashboard").status_code == 200


def test_multiplas_notas_podem_ser_criadas_alternadas_editadas_e_excluidas(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    assert cliente.get("/api/notas").json["notas"] == []
    assert cliente.get("/api/notas/atalho").json["hotkey"] == "CTRL+Y"

    primeira = cliente.post("/api/notas", json={"titulo": "Matemática"})
    segunda = cliente.post("/api/notas", json={"titulo": "Leitura"})
    assert primeira.status_code == 201
    assert segunda.status_code == 201
    primeira_id = primeira.json["nota"]["id"]
    segunda_id = segunda.json["nota"]["id"]

    atualizada = cliente.put(
        f"/api/notas/{primeira_id}",
        json={"titulo": "Álgebra", "conteudo": "Rever equações"},
    )
    assert atualizada.status_code == 200
    assert cliente.get(f"/api/notas/{segunda_id}").json["nota"]["titulo"] == "Leitura"
    lista = cliente.get("/api/notas").json["notas"]
    assert [nota["titulo"] for nota in lista] == ["Álgebra", "Leitura"]

    outra_conta = app.test_client()
    cadastrar_e_entrar(outra_conta, "outra@example.com")
    assert outra_conta.get(f"/api/notas/{primeira_id}").status_code == 404
    assert cliente.delete(f"/api/notas/{primeira_id}").status_code == 200
    assert [nota["id"] for nota in cliente.get("/api/notas").json["notas"]] == [segunda_id]

    assert cliente.put("/api/notas/atalho", json={"hotkey": "CTRL+SHIFT+N"}).json["hotkey"] == "CTRL+SHIFT+N"
    assert cliente.get("/api/notas").json["hotkey"] == "CTRL+SHIFT+N"
    assert cliente.post("/api/notas", json={"titulo": " "}).status_code == 400
    with app.app_context():
        assert db.session.execute(db.select(db.func.count(Nota.id))).scalar_one() == 1


def test_migracao_de_nota_legada_preserva_conteudo_e_atalho(app):
    with app.app_context():
        estudante = Estudante(
            email="nota-legada@example.com",
            senha="scrypt:32768:8:1$legacy$legacy",
        )
        db.session.add(estudante)
        db.session.flush()
        bloco = BlocoNotas(
            estudante_id=estudante.id,
            conteudo="Anotações antigas",
            hotkey="ALT+N",
            notas_migradas=False,
        )
        db.session.add(bloco)
        db.session.commit()

        inicializar_banco()
        notas = db.session.execute(
            db.select(Nota).where(Nota.estudante_id == estudante.id)
        ).scalars().all()
        assert len(notas) == 1
        assert notas[0].titulo == "Minha primeira nota"
        assert notas[0].conteudo == "Anotações antigas"
        assert bloco.conteudo == ""
        assert bloco.hotkey == "ALT+N"

        inicializar_banco()
        assert db.session.execute(
            db.select(db.func.count(Nota.id)).where(Nota.estudante_id == estudante.id)
        ).scalar_one() == 1


def test_perfil_pode_ser_editado_e_foto_trocada_ou_removida(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    assert cliente.get("/perfil").status_code == 200
    assert cliente.get("/api/perfil").json["email"] == "estudante@example.com"

    renomeado = cliente.patch("/api/perfil", data={
        "nome": "Nome Atualizado",
        "remover_foto": "false",
    })
    assert renomeado.status_code == 200
    assert cliente.get("/api/dashboard").json["estudante"]["nome"] == "Nome Atualizado"

    imagem = BytesIO()
    Image.new("RGB", (30, 30), "#287c8e").save(imagem, format="PNG")
    imagem.seek(0)
    atualizado = cliente.patch("/api/perfil", data={
        "nome": "Nome Atualizado",
        "remover_foto": "false",
        "foto_perfil": (imagem, "nova.png"),
    }, content_type="multipart/form-data")
    assert atualizado.status_code == 200
    assert atualizado.json["foto_url"] == "/api/perfil/foto"
    assert cliente.get("/api/perfil/foto").status_code == 200

    removido = cliente.patch("/api/perfil", data={
        "nome": "Nome Atualizado",
        "remover_foto": "true",
    })
    assert removido.status_code == 200
    assert removido.json["foto_url"] is None
    assert cliente.get("/api/perfil/foto").status_code == 404
    assert cliente.patch("/api/perfil", data={"nome": " "}).status_code == 400

    anonimo = app.test_client()
    assert anonimo.get("/perfil").status_code == 302
    assert anonimo.get("/api/perfil").status_code == 401


def test_botao_de_teste_adiciona_100_xp_so_ao_pet_evoluindo(app):
    app.config["DEVELOPER_EMAIL"] = "estudante@example.com"
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    cliente.post("/api/pets/iniciais")
    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "estudante@example.com")
        ).scalar_one()
        pet = db.session.get(Pet, estudante.pet_equipado_id)
        pet.xp_atual = 299
        pet.sincronizar_nivel()
        db.session.commit()

    resposta = cliente.post("/api/pets/teste/ganhar-xp")
    assert resposta.status_code == 200
    assert resposta.json["xp_ganho"] == 100
    assert resposta.json["pet"]["xp_atual"] == 399
    assert resposta.json["pet"]["nivel"] == 4
    assert resposta.json["pet"]["nome"] == "Kakuna"
    assert resposta.json["pet"]["imagem_url"].endswith("kakuna%20evo1%20grup0.png")
    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "estudante@example.com")
        ).scalar_one()
        assert estudante.xp_total == 0


def test_resumo_semanal_soma_estudos_e_foco_e_mostra_xp_total(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    cliente.post("/api/pets/iniciais")

    atividade = cliente.post("/api/agenda", json={
        "data": datetime.now(timezone.utc).date().isoformat(),
        "titulo": "Estudo semanal",
        "duracao_minutos": 60,
    })
    assert atividade.status_code == 201
    assert cliente.post(
        f"/api/agenda/{atividade.json['atividade']['id']}/concluir"
    ).json["xp_ganho"] == 12

    sessao = cliente.post("/api/foco/iniciar").json
    with app.app_context():
        registro = db.session.get(SessaoFoco, sessao["sessao_id"])
        registro.inicio = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=30)
        db.session.commit()
    assert cliente.post(f"/api/foco/encerrar/{sessao['sessao_id']}").json["xp_ganho"] == 12

    resumo = cliente.get("/api/resumo-semanal")
    assert resumo.status_code == 200
    assert resumo.json["horas_estudadas"] == 1.5
    assert resumo.json["xp_ganho"] == 24
    dashboard = cliente.get("/api/dashboard").json
    assert dashboard["estudante"]["xp_total"] == 24
    assert dashboard["pet"]["xp_atual"] == 24
    assert cliente.get("/resumo").status_code == 200


def test_area_desenvolvedor_e_simulacao_sao_restritas_e_contam_como_estudo(app):
    app.config["DEVELOPER_EMAIL"] = "dev@example.com"
    desenvolvedor = app.test_client()
    usuario = app.test_client()
    for cliente, email in (
        (desenvolvedor, "dev@example.com"),
        (usuario, "normal@example.com"),
    ):
        assert cliente.post("/api/auth/cadastro", json={
            "email": email,
            "senha": SENHA_TESTE,
        }).status_code == 201
        login = cliente.post("/api/auth/login", json={
            "email": email,
            "senha": SENHA_TESTE,
        })
        assert login.status_code == 200

    assert desenvolvedor.get("/api/auth/session").json["is_developer"] is True
    assert usuario.get("/api/auth/session").json["is_developer"] is False
    assert desenvolvedor.get("/desenvolvedor").status_code == 200
    assert usuario.get("/desenvolvedor").status_code == 302
    assert usuario.post("/api/pets/teste/ganhar-xp").status_code == 403
    assert usuario.post(
        "/api/desenvolvedor/simular-estudo", json={"horas": 2}
    ).status_code == 403

    desenvolvedor.post("/api/pets/iniciais")
    simulacao = desenvolvedor.post(
        "/api/desenvolvedor/simular-estudo", json={"horas": 2}
    )
    assert simulacao.status_code == 201
    assert simulacao.json["horas_estudadas"] == 2
    assert simulacao.json["xp_ganho"] == 25
    assert simulacao.json["atividade"]["concluido"] is True
    resumo = desenvolvedor.get("/api/resumo-semanal")
    assert resumo.json["horas_estudadas"] == 2
    assert resumo.json["xp_ganho"] == 25
    dashboard = desenvolvedor.get("/api/dashboard").json
    assert dashboard["estudante"]["xp_total"] == 25
    assert dashboard["pet"]["xp_atual"] == 25

    invalida = desenvolvedor.post(
        "/api/desenvolvedor/simular-estudo", json={"horas": 13}
    )
    assert invalida.status_code == 400


def test_encerrar_sessao_de_foco_concede_xp_uma_vez(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    cliente.post("/api/pets/iniciais")
    resposta = cliente.post("/api/foco/iniciar")
    sessao_id = resposta.json["sessao_id"]
    token_api = resposta.json["token_api"]
    with app.app_context():
        sessao = db.session.get(SessaoFoco, sessao_id)
        sessao.inicio = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=4)
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "estudante@example.com")
        ).scalar_one()
        pet = db.session.get(Pet, estudante.pet_equipado_id)
        pet.xp_atual = 720
        pet.nivel = 8
        db.session.commit()

    extensao = app.test_client()
    headers = {"Authorization": f"Bearer {token_api}"}
    status = extensao.get(f"/api/foco/status/{sessao_id}", headers=headers)
    assert status.status_code == 200
    assert 240 <= status.json["tempo_total_minutos"] <= 241
    assert status.json["vezes_distraido"] == 0
    distracao = extensao.post(f"/api/foco/registrar-distracao/{sessao_id}", headers=headers)
    assert distracao.json["vezes_distraido"] == 1
    assert extensao.get(
        f"/api/foco/status/{sessao_id}", headers=headers
    ).json["vezes_distraido"] == 1
    primeira = extensao.post(f"/api/foco/encerrar/{sessao_id}", headers=headers)
    segunda = cliente.post(f"/api/foco/encerrar/{sessao_id}")
    assert primeira.json["xp_ganho"] == 80
    assert segunda.json["xp_ganho"] == 0
    assert extensao.get(f"/api/foco/status/{sessao_id}", headers=headers).status_code == 401
    pet_apos_foco = cliente.get("/api/dashboard").json["pet"]
    assert pet_apos_foco["xp_atual"] == 800
    assert pet_apos_foco["nivel"] == 9
    assert pet_apos_foco["imagem_url"].endswith("beedrill%20evo2%20grup0.png")


def test_sessao_de_foco_ativa_pode_ser_recuperada_e_nao_duplica(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)

    primeira = cliente.post("/api/foco/iniciar")
    assert primeira.status_code == 201
    assert primeira.json["ja_ativa"] is False

    segunda = cliente.post("/api/foco/iniciar")
    assert segunda.status_code == 200
    assert segunda.json["ja_ativa"] is True
    assert segunda.json["sessao_id"] == primeira.json["sessao_id"]
    assert segunda.json["token_api"] == primeira.json["token_api"]
    with app.app_context():
        sessoes_ativas = db.session.execute(
            db.select(db.func.count(SessaoFoco.id)).where(
                SessaoFoco.estudante_id == 1,
                SessaoFoco.modo_ativo.is_(True),
            )
        ).scalar_one()
        assert sessoes_ativas == 1

    recuperada = cliente.get("/api/foco/ativa")
    assert recuperada.status_code == 200
    assert recuperada.json["sessao"]["sessao_id"] == primeira.json["sessao_id"]
    assert recuperada.json["sessao"]["token_api"] == primeira.json["token_api"]
    assert recuperada.json["sessao"]["vezes_distraido"] == 0

    assert cliente.post(f"/api/foco/encerrar/{primeira.json['sessao_id']}").status_code == 200
    assert cliente.get("/api/foco/ativa").json["sessao"] is None


def test_materias_sao_cadastradas_editadas_e_contabilizam_horas_semanais(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)

    assert cliente.get("/materias").status_code == 200
    assert cliente.get("/api/materias").json["materias"] == []

    criada = cliente.post("/api/materias", json={"nome": "Matemática"})
    assert criada.status_code == 201
    materia = criada.json["materia"]
    materia_id = materia["id"]
    assert materia["horas_estudadas_semana"] == 0
    assert cliente.post("/api/materias", json={"nome": " matemática "}).status_code == 400

    foco = cliente.post("/api/foco/iniciar", json={"materia_id": materia_id})
    assert foco.status_code == 201
    sessao_id = foco.json["sessao_id"]
    assert foco.json["materia_nome"] == "Matemática"
    with app.app_context():
        sessao = db.session.get(SessaoFoco, sessao_id)
        sessao.inicio = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            minutes=90
        )
        db.session.commit()

    materias = cliente.get("/api/materias").json["materias"]
    assert 1.49 <= materias[0]["horas_estudadas_semana"] <= 1.51

    editada = cliente.patch(
        f"/api/materias/{materia_id}", json={"nome": "Matemática avançada"}
    )
    assert editada.status_code == 200
    assert editada.json["materia"]["nome"] == "Matemática avançada"
    assert editada.json["materia"]["minutos_estudados_semana"] >= 90
    assert cliente.get("/api/foco/ativa").json["sessao"]["materia_nome"] == "Matemática avançada"


def test_materia_e_opcional_e_nao_pode_ser_usada_por_outro_estudante(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    materia = cliente.post("/api/materias", json={"nome": "História"}).json["materia"]

    outro = app.test_client()
    cadastrar_e_entrar(
        outro, email="outro@example.com", senha="OutroEstudante3!"
    )
    assert outro.post(
        "/api/foco/iniciar", json={"materia_id": materia["id"]}
    ).status_code == 400
    assert outro.patch(
        f"/api/materias/{materia['id']}", json={"nome": "História privada"}
    ).status_code == 404
    sessao_sem_materia = outro.post("/api/foco/iniciar")
    assert sessao_sem_materia.status_code == 201
    assert sessao_sem_materia.json["materia_id"] is None


def test_historico_foco_filtra_periodo_mostra_detalhe_e_isola_estudantes(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    criada = cliente.post("/api/materias", json={"nome": "Física"})
    materia_id = criada.json["materia"]["id"]
    inicio = datetime(2026, 10, 12, 9, 30)
    fim = datetime(2026, 10, 12, 10, 35)
    with app.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(
                Estudante.email == "estudante@example.com"
            )
        ).scalar_one()
        sessao = SessaoFoco(
            inicio=inicio,
            fim=fim,
            modo_ativo=False,
            vezes_distraido=2,
            tempo_total_minutos=65,
            xp_ganho=25,
            estudante_id=estudante.id,
            materia_id=materia_id,
        )
        ativa = SessaoFoco(
            inicio=datetime(2026, 10, 12, 11),
            modo_ativo=True,
            vezes_distraido=0,
            estudante_id=estudante.id,
        )
        db.session.add_all([sessao, ativa])
        db.session.commit()
        sessao_id = sessao.id

    assert cliente.get("/historico-foco").status_code == 200
    historico = cliente.get("/api/foco/historico")
    assert historico.status_code == 200
    assert len(historico.json["sessoes"]) == 1
    assert historico.json["sessoes"][0] == {
        "id": sessao_id,
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "duracao_minutos": 65,
        "vezes_distraido": 2,
        "xp_ganho": 25,
        "xp_base": 25,
        "xp_bonus_meta": 0,
        "materia": "Física",
    }
    assert cliente.get(
        "/api/foco/historico?inicio=2026-10-12&fim=2026-10-12"
    ).json["sessoes"] == historico.json["sessoes"]
    assert cliente.get(
        "/api/foco/historico?inicio=2026-10-13"
    ).json["sessoes"] == []
    assert cliente.get(
        "/api/foco/historico?inicio=2026-10-13&fim=2026-10-12"
    ).status_code == 400
    assert cliente.get(
        "/api/foco/historico?inicio=12-10-2026"
    ).status_code == 400

    detalhe = cliente.get(f"/api/foco/historico/{sessao_id}")
    assert detalhe.status_code == 200
    assert detalhe.json["sessao"]["materia"] == "Física"
    assert "token_api" not in detalhe.json["sessao"]

    outro = app.test_client()
    cadastrar_e_entrar(
        outro, email="outro@example.com", senha="OutroEstudante3!"
    )
    assert outro.get("/api/foco/historico").json["sessoes"] == []
    assert outro.get(f"/api/foco/historico/{sessao_id}").status_code == 404
    assert app.test_client().get("/api/foco/historico").status_code == 401


def test_migracao_adiciona_materia_opcional_a_sessoes_existentes(app):
    with app.app_context():
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "DROP TABLE sessoes_de_foco"
            )
            conexao.exec_driver_sql(
                """CREATE TABLE sessoes_de_foco (
                    id INTEGER PRIMARY KEY,
                    inicio DATETIME,
                    fim DATETIME,
                    modo_ativo BOOLEAN,
                    vezes_distraido INTEGER,
                    tempo_total_minutos INTEGER,
                    xp_ganho INTEGER DEFAULT 0,
                    token_api VARCHAR(64),
                    estudante_id INTEGER NOT NULL
                )"""
            )
        inicializar_banco()
        colunas = {
            coluna["name"]
            for coluna in inspect(db.engine).get_columns("sessoes_de_foco")
        }
        assert {"materia_id", "xp_bonus_meta", "token_api"} <= colunas


def test_meta_diaria_concede_bonus_uma_vez_e_atualiza_xp_estudante_e_pet(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    cliente.post("/api/pets/iniciais")
    assert cliente.get("/metas").status_code == 200
    inicial = cliente.get("/api/metas").json
    assert inicial["meta_diaria_minutos"] == 0
    assert inicial["diaria"]["minutos_estudados"] == 0

    configurada = cliente.put("/api/metas", json={
        "meta_diaria_minutos": 60,
        "meta_semanal_minutos": 0,
    })
    assert configurada.status_code == 200
    assert configurada.json["meta_diaria_minutos"] == 60
    assert configurada.json["diaria"]["bonus_xp"] == 10

    primeira = cliente.post("/api/foco/iniciar").json
    with app.app_context():
        sessao = db.session.get(SessaoFoco, primeira["sessao_id"])
        sessao.inicio = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            minutes=60
        )
        db.session.commit()
    encerrada = cliente.post(f"/api/foco/encerrar/{primeira['sessao_id']}")
    assert encerrada.status_code == 200
    assert encerrada.json["xp_base"] == 25
    assert encerrada.json["xp_bonus_meta"] == 10
    assert encerrada.json["xp_ganho"] == 35

    progresso = cliente.get("/api/metas").json
    assert progresso["diaria"]["atingida"] is True
    assert progresso["diaria"]["bonus_concedido"] is True
    assert progresso["diaria"]["bonus_xp"] == 10
    dashboard = cliente.get("/api/dashboard").json
    assert dashboard["estudante"]["xp_total"] == 35
    assert dashboard["pet"]["xp_atual"] == 35

    segunda = cliente.post("/api/foco/iniciar").json
    with app.app_context():
        sessao = db.session.get(SessaoFoco, segunda["sessao_id"])
        sessao.inicio = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            minutes=30
        )
        db.session.commit()
    novamente = cliente.post(f"/api/foco/encerrar/{segunda['sessao_id']}")
    assert novamente.json["xp_bonus_meta"] == 0
    assert novamente.json["xp_ganho"] == 12
    repetida = cliente.post(f"/api/foco/encerrar/{primeira['sessao_id']}")
    assert repetida.status_code == 200
    assert repetida.json["ja_concluida"] is True
    assert repetida.json["xp_ganho"] == 0
    assert repetida.json["xp_base"] == 0
    assert repetida.json["xp_bonus_meta"] == 0
    with app.app_context():
        quantidade_bonus = db.session.execute(
            db.select(db.func.count(BonusMeta.id)).where(
                BonusMeta.estudante_id == 1,
                BonusMeta.tipo == "diaria",
            )
        ).scalar_one()
        assert quantidade_bonus == 1
        estudante = db.session.get(Estudante, 1)
        assert estudante.xp_total == 47


def test_meta_semanal_concede_bonus_maximo_ao_atingir_quatro_horas(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    cliente.post("/api/pets/iniciais")
    resposta = cliente.put("/api/metas", json={
        "meta_diaria_minutos": 0,
        "meta_semanal_minutos": 240,
    })
    assert resposta.status_code == 200
    assert resposta.json["semanal"]["bonus_xp"] == 20

    sessao = cliente.post("/api/foco/iniciar").json
    with app.app_context():
        registro = db.session.get(SessaoFoco, sessao["sessao_id"])
        registro.inicio = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            hours=4
        )
        db.session.commit()
    encerrada = cliente.post(f"/api/foco/encerrar/{sessao['sessao_id']}")
    assert encerrada.json["xp_base"] == 100
    assert encerrada.json["xp_bonus_meta"] == 20
    assert encerrada.json["xp_ganho"] == 120
    historico = cliente.get(
        f"/api/foco/historico/{sessao['sessao_id']}"
    ).json["sessao"]
    assert historico["xp_bonus_meta"] == 20


def test_configuracao_de_metas_tem_limites_e_nao_permitem_acumular_diaria_semanal(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    assert cliente.put("/api/metas", json={
        "meta_diaria_minutos": 60,
        "meta_semanal_minutos": 60,
    }).status_code == 400
    assert cliente.put("/api/metas", json={
        "meta_diaria_minutos": 1441,
        "meta_semanal_minutos": 0,
    }).status_code == 400
    assert cliente.put("/api/metas", json={
        "meta_diaria_minutos": 0,
        "meta_semanal_minutos": 10081,
    }).status_code == 400
    assert cliente.put("/api/metas", json={
        "meta_diaria_minutos": 20.5,
        "meta_semanal_minutos": 0,
    }).status_code == 400


def test_bonus_meta_escala_dez_xp_em_uma_hora_ate_vinte_em_quatro_horas():
    assert calcular_xp_bonus_meta(0) == 0
    assert calcular_xp_bonus_meta(30) == 5
    assert calcular_xp_bonus_meta(60) == 10
    assert calcular_xp_bonus_meta(150) == 15
    assert calcular_xp_bonus_meta(240) == 20
    assert calcular_xp_bonus_meta(1440) == 20


def test_pet_evolui_nos_niveis_definidos_e_para_no_nivel_dez():
    grupo_zero = Pet(nome="Weedle", linha_evolutiva="grup0", xp_atual=299)
    assert grupo_zero.nome_atual == "Weedle"
    assert grupo_zero.calcular_nivel(299) == 3
    grupo_zero.xp_atual = 300
    grupo_zero.sincronizar_nivel()
    assert grupo_zero.nome_atual == "Kakuna"
    assert grupo_zero.nivel == 4
    assert grupo_zero.imagem_url.endswith("kakuna%20evo1%20grup0.png")
    grupo_zero.xp_atual = 800
    grupo_zero.sincronizar_nivel()
    assert grupo_zero.nome_atual == "Beedrill"
    assert grupo_zero.nivel == 9
    assert grupo_zero.imagem_url.endswith("beedrill%20evo2%20grup0.png")
    grupo_zero.xp_atual = 900
    grupo_zero.sincronizar_nivel()
    assert grupo_zero.nivel == 10
    assert grupo_zero.xp_para_proximo_nivel == 0

    grupo_um = Pet(nome="Elekid", linha_evolutiva="grup1", xp_atual=300)
    grupo_um.sincronizar_nivel()
    assert grupo_um.nome_atual == "Electabuzz"
    assert grupo_um.imagem_url.endswith("electabuzz%20evo1%20grup1.png")
    grupo_um.xp_atual = 800
    grupo_um.sincronizar_nivel()
    assert grupo_um.nome_atual == "Electivire"
    assert grupo_um.imagem_url.endswith("electivire%20evo2%20grup1.png")


def test_dashboard_soma_xp_de_todos_os_pets_e_atualiza_nome_apos_evolucao(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    pets = cliente.post("/api/pets/iniciais").json["pets"]

    with app.app_context():
        primeiro = db.session.get(Pet, pets[0]["id"])
        segundo = db.session.get(Pet, pets[1]["id"])
        primeiro.xp_atual = 300
        primeiro.sincronizar_nivel()
        segundo.xp_atual = 800
        segundo.sincronizar_nivel()
        db.session.commit()

    dashboard = cliente.get("/api/dashboard").json
    assert dashboard["estudante"]["xp_total"] == 1100
    assert dashboard["pet"]["nome"] == "Kakuna"
    inventario = cliente.get("/api/pets").json["pets"]
    assert [pet["nome"] for pet in inventario] == ["Kakuna", "Electivire"]


def test_xp_de_atividades_e_sessoes_respeita_limites_e_descontos():
    assert calcular_xp_atividade(0) == 0
    assert calcular_xp_atividade(60) == 12
    assert calcular_xp_atividade(240) == 50
    assert calcular_xp_atividade(1440) == 50

    assert calcular_xp_foco(0, 0) == 0
    assert calcular_xp_foco(60, 0) == 25
    assert calcular_xp_foco(240, 0) == 100
    assert calcular_xp_foco(300, 0) == 100
    assert calcular_xp_foco(240, 1) == 80
    assert calcular_xp_foco(240, 5) == 0


def test_xp_real_de_atividade_fica_limitado_a_50(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    cliente.post("/api/pets/iniciais")

    atividade = cliente.post("/api/agenda", json={
        "data": datetime.now(timezone.utc).date().isoformat(),
        "titulo": "Estudo longo",
        "duracao_minutos": 1440,
    })
    assert atividade.status_code == 201
    assert atividade.json["atividade"]["xp"] == 50
    concluida = cliente.post(
        f"/api/agenda/{atividade.json['atividade']['id']}/concluir"
    )
    assert concluida.json["xp_ganho"] == 50

    atividade_zero = cliente.post("/api/agenda", json={
        "data": datetime.now(timezone.utc).date().isoformat(),
        "titulo": "Atividade sem duração",
        "duracao_minutos": 0,
    })
    concluida_zero = cliente.post(
        f"/api/agenda/{atividade_zero.json['atividade']['id']}/concluir"
    )
    assert concluida_zero.json["xp_ganho"] == 0


def test_migracao_preserva_xp_historico_de_atividades_concluidas(app):
    with app.app_context():
        estudante = Estudante(
            email="legado-xp@example.com",
            senha="scrypt:32768:8:1$legacy$legacy",
        )
        db.session.add(estudante)
        db.session.flush()
        agenda = Agenda(estudante_id=estudante.id)
        db.session.add(agenda)
        db.session.flush()
        estudo = Estudo(
            titulo="Atividade antiga",
            duracao_minutos=40,
            concluido=True,
            xp_ganho=0,
            agenda_id=agenda.id,
        )
        db.session.add(estudo)
        db.session.flush()
        estudo_id = estudo.id
        db.session.commit()

        with db.engine.begin() as conexao:
            conexao.exec_driver_sql("ALTER TABLE estudos DROP COLUMN xp_ganho")

        inicializar_banco()
        db.session.expire_all()
        migrado = db.session.get(Estudo, estudo_id)
        assert migrado.xp_ganho == 60


def test_lembrete_de_atividade_e_opcional_e_disparado_uma_vez(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    data = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    sem_lembrete = cliente.post("/api/agenda", json={
        "titulo": "Estudo sem lembrete",
        "data": data,
        "duracao_minutos": 30,
    })
    assert sem_lembrete.status_code == 201
    assert sem_lembrete.json["atividade"]["lembrete_em"] is None

    lembrete_em = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    com_lembrete = cliente.post("/api/agenda", json={
        "titulo": "Revisar biologia",
        "data": data,
        "duracao_minutos": 45,
        "lembrete_em": lembrete_em,
    })
    assert com_lembrete.status_code == 201
    atividade = com_lembrete.json["atividade"]
    atividade_id = atividade["id"]
    assert atividade["lembrete_em"] is not None
    assert cliente.get("/api/agenda/lembretes-vencidos").json["lembretes"] == []

    with app.app_context():
        estudo = db.session.get(Estudo, atividade_id)
        estudo.lembrete_em = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            seconds=1
        )
        db.session.commit()

    vencidos = cliente.get("/api/agenda/lembretes-vencidos")
    assert vencidos.status_code == 200
    assert [item["id"] for item in vencidos.json["lembretes"]] == [atividade_id]
    assert cliente.post(
        f"/api/agenda/{atividade_id}/lembrete-enviado"
    ).status_code == 200
    assert cliente.get("/api/agenda/lembretes-vencidos").json["lembretes"] == []
    assert cliente.post(
        f"/api/agenda/{atividade_id}/lembrete-enviado"
    ).status_code == 404


def test_lembrete_nao_aceita_horario_invalido_ou_passado(app):
    cliente = app.test_client()
    cadastrar_e_entrar(cliente)
    data = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    base = {"titulo": "Tarefa", "data": data, "duracao_minutos": 20}

    passado = cliente.post("/api/agenda", json={
        **base,
        "lembrete_em": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
    })
    assert passado.status_code == 400
    invalido = cliente.post("/api/agenda", json={
        **base,
        "lembrete_em": "data-hora-invalida",
    })
    assert invalido.status_code == 400


def test_migracao_adiciona_colunas_de_lembrete_a_estudos_existentes(app):
    with app.app_context():
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql("ALTER TABLE estudos DROP COLUMN lembrete_em")
            conexao.exec_driver_sql(
                "ALTER TABLE estudos DROP COLUMN lembrete_notificado"
            )
        inicializar_banco()
        colunas = {
            coluna["name"] for coluna in inspect(db.engine).get_columns("estudos")
        }
        assert {"lembrete_em", "lembrete_notificado"} <= colunas


def test_migracao_hash_senhas_preserva_dados(tmp_path):
    caminho = tmp_path / "legado.db"
    conexao = sqlite3.connect(caminho)
    conexao.execute("""CREATE TABLE estudantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email VARCHAR(120) NOT NULL UNIQUE,
        senha VARCHAR(128) NOT NULL,
        xp_total INTEGER DEFAULT 0,
        tema_de_cores VARCHAR(50) DEFAULT 'default',
        meta_diaria_minutos INTEGER DEFAULT 0,
        assinatura BOOLEAN DEFAULT 0,
        tribo_id INTEGER,
        pet_equipado_id INTEGER
    )""")
    conexao.execute(
        "INSERT INTO estudantes (email, senha) VALUES (?, ?)",
        ("legado@example.com", "senha-antiga"),
    )
    conexao.commit()
    conexao.close()

    app_legado = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{caminho}",
    })
    cliente = app_legado.test_client()
    resposta = cliente.post("/api/auth/login", json={
        "email": "legado@example.com",
        "senha": "senha-antiga",
    })
    assert resposta.status_code == 200
    with app_legado.app_context():
        estudante = db.session.execute(
            db.select(Estudante).where(Estudante.email == "legado@example.com")
        ).scalar_one()
        assert estudante.senha != "senha-antiga"
        assert estudante.foto_perfil is None
        db.session.remove()
        db.session.execute(db.update(Estudante).values(pet_equipado_id=None))
        db.session.execute(db.update(Pet).values(estudante_id=None))
        db.session.commit()
        db.drop_all()
        db.engine.dispose()
