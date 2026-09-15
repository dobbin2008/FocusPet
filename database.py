import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Protocol

from flask import current_app, g


class DatabaseGateway(Protocol):
    def execute(self, sql, parameters=()): ...
    def commit(self): ...
    def rollback(self): ...


SCHEMA = """
CREATE TABLE IF NOT EXISTS tribos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia VARCHAR(120) NOT NULL
);
CREATE TABLE IF NOT EXISTS estudantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) NOT NULL UNIQUE,
    senha VARCHAR(128) NOT NULL,
    xp_total INTEGER DEFAULT 0,
    tema_de_cores VARCHAR(50) DEFAULT 'default',
    meta_diaria_minutos INTEGER DEFAULT 0,
    assinatura BOOLEAN DEFAULT 0,
    tribo_id INTEGER,
    pet_equipado_id INTEGER
);
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(120) NOT NULL,
    nivel INTEGER DEFAULT 1,
    descricao VARCHAR(255),
    imagem VARCHAR(255),
    imagem_nivel_1 VARCHAR(255),
    imagem_nivel_2 VARCHAR(255),
    imagem_nivel_3 VARCHAR(255),
    xp_atual INTEGER DEFAULT 0,
    eh_padrao BOOLEAN DEFAULT 0,
    estudante_id INTEGER,
    tribo_id INTEGER
);
CREATE TABLE IF NOT EXISTS agendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_atual DATETIME,
    estudante_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS estudos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL DEFAULT 'Estudo',
    inicio DATETIME,
    fim DATETIME,
    duracao_minutos INTEGER DEFAULT 0,
    concluido BOOLEAN DEFAULT 0,
    agenda_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS blocos_de_notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conteudo TEXT,
    hotkey VARCHAR(20),
    estudante_id INTEGER NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS sessoes_de_foco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inicio DATETIME,
    fim DATETIME,
    modo_ativo BOOLEAN DEFAULT 0,
    vezes_distraido INTEGER DEFAULT 0,
    tempo_total_minutos INTEGER DEFAULT 0,
    xp_ganho INTEGER DEFAULT 0,
    estudante_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS listas_bloqueadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url VARCHAR(255) NOT NULL,
    descricao VARCHAR(255),
    estudante_id INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS resumos_semanais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_inicio DATETIME,
    data_fim DATETIME,
    horas_estudadas FLOAT DEFAULT 0,
    vezes_distraido INTEGER DEFAULT 0,
    progresso_pet FLOAT DEFAULT 0,
    estudante_id INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_estudos_agenda_inicio ON estudos(agenda_id, inicio);
CREATE INDEX IF NOT EXISTS idx_blacklist_estudante ON listas_bloqueadas(estudante_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_estudante ON sessoes_de_foco(estudante_id);
CREATE VIEW IF NOT EXISTS agenda_atividades AS
SELECT estudos.id, estudos.titulo, estudos.inicio, estudos.fim,
       estudos.duracao_minutos, estudos.concluido, estudos.agenda_id,
       agendas.estudante_id
FROM estudos
JOIN agendas ON agendas.id = estudos.agenda_id;
"""


def abrir_conexao(caminho):
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco(caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    conexao = abrir_conexao(caminho)
    conexao.executescript(SCHEMA)
    colunas = {linha[1] for linha in conexao.execute("PRAGMA table_info(sessoes_de_foco)")}
    if "xp_ganho" not in colunas:
        conexao.execute("ALTER TABLE sessoes_de_foco ADD COLUMN xp_ganho INTEGER DEFAULT 0")
    conexao.commit()
    conexao.close()


def obter_banco():
    if "banco" not in g:
        caminho = current_app.config["DATABASE"]
        g.banco = abrir_conexao(caminho)
    return g.banco


def get_database() -> DatabaseGateway:
    return obter_banco()


def fechar_banco(_erro=None):
    banco = g.pop("banco", None)
    if banco is not None:
        banco.close()


def registro(linha):
    if linha is None:
        return None
    return SimpleNamespace(**dict(linha))


@contextmanager
def transacao():
    banco = obter_banco()
    try:
        yield banco
        banco.commit()
    except Exception:
        banco.rollback()
        raise


def agora():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat(sep=" ")
