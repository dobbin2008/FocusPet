from datetime import datetime, time, timedelta

from sqlalchemy import func

from backend.extensions import db
from backend.models import BonusMeta, MetaEstudo, SessaoFoco
from backend.repositories.base import BaseRepository


class MetasRepository(BaseRepository):
    def obter(self, estudante_id):
        consulta = db.select(MetaEstudo).where(
            MetaEstudo.estudante_id == estudante_id
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def salvar(
        self, estudante_id, meta_diaria_minutos, meta_semanal_minutos,
        meta_semanal_dias=0,
    ):
        meta = self.obter(estudante_id)
        if meta is None:
            meta = MetaEstudo(estudante_id=estudante_id)
            db.session.add(meta)
        meta.meta_diaria_minutos = meta_diaria_minutos
        meta.meta_semanal_minutos = meta_semanal_minutos
        meta.meta_semanal_dias = meta_semanal_dias
        self.salvar_alteracoes()
        return meta

    def minutos_foco_no_periodo(self, estudante_id, inicio, fim):
        consulta = db.select(
            func.coalesce(func.sum(SessaoFoco.tempo_total_minutos), 0)
        ).where(
            SessaoFoco.estudante_id == estudante_id,
            SessaoFoco.modo_ativo.is_(False),
            SessaoFoco.fim >= inicio,
            SessaoFoco.fim < fim,
        )
        return db.session.execute(consulta).scalar_one()

    def dias_foco_no_periodo(self, estudante_id, inicio, fim):
        consulta = db.select(
            func.count(func.distinct(func.date(SessaoFoco.fim)))
        ).where(
            SessaoFoco.estudante_id == estudante_id,
            SessaoFoco.modo_ativo.is_(False),
            SessaoFoco.fim >= inicio,
            SessaoFoco.fim < fim,
        )
        return db.session.execute(consulta).scalar_one()

    def bonus_ja_concedido(self, estudante_id, tipo, periodo_inicio):
        consulta = db.select(BonusMeta.id).where(
            BonusMeta.estudante_id == estudante_id,
            BonusMeta.tipo == tipo,
            BonusMeta.periodo_inicio == periodo_inicio,
        )
        return db.session.execute(consulta).scalar_one_or_none() is not None

    def listar_bonus(self, estudante_id, inicio_dia, inicio_semana):
        consulta = db.select(BonusMeta).where(
            BonusMeta.estudante_id == estudante_id,
            db.or_(
                db.and_(
                    BonusMeta.tipo == "diaria",
                    BonusMeta.periodo_inicio == inicio_dia,
                ),
                db.and_(
                    BonusMeta.tipo == "semanal",
                    BonusMeta.periodo_inicio == inicio_semana,
                ),
            ),
        )
        return db.session.execute(consulta).scalars().all()

    def progresso_atual(self, estudante_id, agora):
        inicio_dia = agora.date()
        inicio_semana = inicio_dia - timedelta(days=inicio_dia.weekday())
        inicio_dia_dt = datetime.combine(inicio_dia, time.min)
        inicio_semana_dt = datetime.combine(inicio_semana, time.min)
        fim_dia = inicio_dia_dt + timedelta(days=1)
        fim_semana = inicio_semana_dt + timedelta(days=7)
        return {
            "inicio_dia": inicio_dia,
            "inicio_semana": inicio_semana,
            "minutos_diarios": self.minutos_foco_no_periodo(
                estudante_id, inicio_dia_dt, fim_dia
            ),
            "minutos_semanais": self.minutos_foco_no_periodo(
                estudante_id, inicio_semana_dt, fim_semana
            ),
            "dias_semanais": self.dias_foco_no_periodo(
                estudante_id, inicio_semana_dt, fim_semana
            ),
        }
