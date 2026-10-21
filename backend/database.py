from flask import current_app
from sqlalchemy import event, inspect, text
from werkzeug.security import generate_password_hash

from backend.extensions import db
from backend.models import BlocoNotas, Estudante, MetaEstudo, Nota


def _ativar_chaves_estrangeiras(conexao, _registro):
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _migrar_colunas_legadas():
    inspector = inspect(db.engine)
    tabelas = set(inspector.get_table_names())
    if "estudantes" not in tabelas:
        return
    colunas = {coluna["name"] for coluna in inspector.get_columns("estudantes")}
    if "nome_exibicao" not in colunas:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE estudantes ADD COLUMN nome_exibicao VARCHAR(120)"
            )
    if "foto_perfil" not in colunas:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE estudantes ADD COLUMN foto_perfil VARCHAR(255)"
            )
    colunas_notas = {coluna["name"] for coluna in inspector.get_columns("blocos_de_notas")}
    if "notas_migradas" not in colunas_notas:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE blocos_de_notas ADD COLUMN notas_migradas BOOLEAN NOT NULL DEFAULT 0"
            )
    colunas_sessao = {coluna["name"] for coluna in inspector.get_columns("sessoes_de_foco")}
    if "xp_ganho" not in colunas_sessao:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE sessoes_de_foco ADD COLUMN xp_ganho INTEGER DEFAULT 0"
            )
    if "token_api" not in colunas_sessao:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE sessoes_de_foco ADD COLUMN token_api VARCHAR(64)"
            )
    if "materia_id" not in colunas_sessao:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE sessoes_de_foco ADD COLUMN materia_id INTEGER "
                "REFERENCES materias(id) ON DELETE SET NULL"
            )
    if "xp_bonus_meta" not in colunas_sessao:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE sessoes_de_foco ADD COLUMN xp_bonus_meta "
                "INTEGER NOT NULL DEFAULT 0"
            )
    colunas_estudo = {coluna["name"] for coluna in inspector.get_columns("estudos")}
    if "xp_ganho" not in colunas_estudo:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE estudos ADD COLUMN xp_ganho INTEGER NOT NULL DEFAULT 0"
            )
            conexao.exec_driver_sql(
                """UPDATE estudos
                SET xp_ganho = CASE
                    WHEN COALESCE(duracao_minutos, 0) * 1.5 < 10 THEN 10
                    ELSE CAST(COALESCE(duracao_minutos, 0) * 1.5 AS INTEGER)
                END
                WHERE concluido = 1"""
            )
    if "lembrete_em" not in colunas_estudo:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE estudos ADD COLUMN lembrete_em DATETIME"
            )
    if "lembrete_notificado" not in colunas_estudo:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE estudos ADD COLUMN lembrete_notificado BOOLEAN "
                "NOT NULL DEFAULT 0"
            )
    colunas_pets = {coluna["name"] for coluna in inspector.get_columns("pets")}
    if "linha_evolutiva" not in colunas_pets:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                "ALTER TABLE pets ADD COLUMN linha_evolutiva VARCHAR(20) NOT NULL DEFAULT 'grup0'"
            )
    with db.engine.begin() as conexao:
        conexao.exec_driver_sql(
            "UPDATE pets SET nivel = MIN(10, CAST(COALESCE(xp_atual, 0) / 100 AS INTEGER) + 1)"
        )
    with db.engine.begin() as conexao:
        conexao.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_sessoes_token_api "
            "ON sessoes_de_foco(token_api) WHERE token_api IS NOT NULL"
        )


def _migrar_senhas_legadas():
    estudantes = db.session.execute(
        text("SELECT id, senha FROM estudantes")
    ).all()
    for estudante_id, senha in estudantes:
        if not senha.startswith(("scrypt:", "pbkdf2:")):
            db.session.execute(
                text("UPDATE estudantes SET senha = :senha WHERE id = :id"),
                {"senha": generate_password_hash(senha), "id": estudante_id},
            )


def _migrar_metas_diarias_legadas():
    estudantes = db.session.execute(
        db.select(Estudante).where(Estudante.meta_diaria_minutos > 0)
    ).scalars()
    for estudante in estudantes:
        meta = db.session.execute(
            db.select(MetaEstudo).where(
                MetaEstudo.estudante_id == estudante.id
            )
        ).scalar_one_or_none()
        if meta is None:
            db.session.add(MetaEstudo(
                estudante_id=estudante.id,
                meta_diaria_minutos=estudante.meta_diaria_minutos,
                meta_semanal_minutos=0,
            ))


def _criar_view_agenda():
    views = set(inspect(db.engine).get_view_names())
    if "agenda_atividades" not in views:
        with db.engine.begin() as conexao:
            conexao.exec_driver_sql(
                """CREATE VIEW agenda_atividades AS
                SELECT estudos.id, estudos.titulo, estudos.inicio, estudos.fim,
                       estudos.duracao_minutos, estudos.concluido, estudos.agenda_id,
                       agendas.estudante_id
                FROM estudos JOIN agendas ON agendas.id = estudos.agenda_id"""
            )


def inicializar_banco():
    engine = db.engine
    if engine.dialect.name == "sqlite" and not event.contains(
        engine, "connect", _ativar_chaves_estrangeiras
    ):
        event.listen(engine, "connect", _ativar_chaves_estrangeiras)
    db.create_all()
    _migrar_colunas_legadas()
    for bloco in db.session.execute(
        db.select(BlocoNotas).where(BlocoNotas.notas_migradas.is_(False))
    ).scalars():
        conteudo = bloco.conteudo or ""
        if conteudo.strip():
            db.session.add(Nota(
                estudante_id=bloco.estudante_id,
                titulo="Minha primeira nota",
                conteudo=conteudo,
            ))
        bloco.conteudo = ""
        bloco.notas_migradas = True
    _criar_view_agenda()
    _migrar_senhas_legadas()
    _migrar_metas_diarias_legadas()

    db.session.commit()


__all__ = ["db", "inicializar_banco"]