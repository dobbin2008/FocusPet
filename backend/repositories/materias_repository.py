from datetime import datetime, timedelta, timezone

from backend.extensions import db
from backend.models import Materia, SessaoFoco
from backend.repositories.base import BaseRepository


class MateriasRepository(BaseRepository):
    def listar_do_estudante(self, estudante_id):
        consulta = (
            db.select(Materia)
            .where(Materia.estudante_id == estudante_id)
            .order_by(Materia.nome.collate("NOCASE"), Materia.id)
        )
        return db.session.execute(consulta).scalars().all()

    def buscar_do_estudante(self, estudante_id, materia_id):
        consulta = db.select(Materia).where(
            Materia.id == materia_id,
            Materia.estudante_id == estudante_id,
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def nome_em_uso(self, estudante_id, nome, excluir_id=None):
        consulta = db.select(Materia.id).where(
            Materia.estudante_id == estudante_id,
            db.func.lower(Materia.nome) == nome.lower(),
        )
        if excluir_id is not None:
            consulta = consulta.where(Materia.id != excluir_id)
        return db.session.execute(consulta).first() is not None

    def minutos_estudados_esta_semana(self, estudante_id):
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        inicio_semana = (agora - timedelta(days=agora.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        fim_semana = inicio_semana + timedelta(days=7)
        consulta = (
            db.select(SessaoFoco)
            .where(
                SessaoFoco.estudante_id == estudante_id,
                SessaoFoco.materia_id.is_not(None),
                SessaoFoco.inicio >= inicio_semana,
                SessaoFoco.inicio < fim_semana,
            )
            .order_by(SessaoFoco.inicio)
        )
        sessoes = db.session.execute(consulta).scalars().all()
        minutos_por_materia = {}
        for sessao in sessoes:
            minutos_por_materia[sessao.materia_id] = (
                minutos_por_materia.get(sessao.materia_id, 0)
                + sessao.minutos_estudados
            )
        return minutos_por_materia
