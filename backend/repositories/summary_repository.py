from sqlalchemy import func

from backend.extensions import db
from backend.models import Agenda, Estudo, ResumoSemanal, SessaoFoco
from backend.repositories.base import BaseRepository


class SummaryRepository(BaseRepository):
    def gerar(self, estudante_id, inicio, fim, progresso_pet):
        minutos_agenda = db.session.execute(
            db.select(func.coalesce(func.sum(Estudo.duracao_minutos), 0))
            .join(Agenda, Estudo.agenda_id == Agenda.id)
            .where(
                Agenda.estudante_id == estudante_id,
                Estudo.concluido.is_(True),
                Estudo.inicio >= inicio,
                Estudo.inicio < fim,
            )
        ).scalar_one()
        minutos_foco = db.session.execute(
            db.select(func.coalesce(func.sum(SessaoFoco.tempo_total_minutos), 0)).where(
                SessaoFoco.estudante_id == estudante_id,
                SessaoFoco.fim >= inicio,
                SessaoFoco.fim < fim,
            )
        ).scalar_one()
        distracoes = db.session.execute(
            db.select(func.coalesce(func.sum(SessaoFoco.vezes_distraido), 0)).where(
                SessaoFoco.estudante_id == estudante_id,
                SessaoFoco.fim >= inicio,
                SessaoFoco.fim < fim,
            )
        ).scalar_one()
        xp_agenda = db.session.execute(
            db.select(func.coalesce(func.sum(Estudo.xp_ganho), 0))
            .join(Agenda, Estudo.agenda_id == Agenda.id)
            .where(
                Agenda.estudante_id == estudante_id,
                Estudo.concluido.is_(True),
                Estudo.inicio >= inicio,
                Estudo.inicio < fim,
            )
        ).scalar_one()
        xp_foco = db.session.execute(
            db.select(func.coalesce(func.sum(SessaoFoco.xp_ganho), 0)).where(
                SessaoFoco.estudante_id == estudante_id,
                SessaoFoco.fim >= inicio,
                SessaoFoco.fim < fim,
            )
        ).scalar_one()
        resumo = db.session.execute(
            db.select(ResumoSemanal).where(
                ResumoSemanal.estudante_id == estudante_id,
                ResumoSemanal.data_inicio == inicio,
            )
        ).scalar_one_or_none()
        if resumo is None:
            resumo = ResumoSemanal(estudante_id=estudante_id, data_inicio=inicio)
        resumo.data_fim = fim
        resumo.horas_estudadas = (minutos_agenda + minutos_foco) / 60
        resumo.vezes_distraido = distracoes
        resumo.progresso_pet = progresso_pet
        db.session.add(resumo)
        self.salvar_alteracoes()
        return resumo, xp_agenda + xp_foco