from datetime import datetime, timezone

from sqlalchemy import func, update

from backend.extensions import db
from backend.models import Agenda, Estudante, Estudo, Pet
from backend.repositories.base import BaseRepository
from backend.xp import calcular_xp_atividade


class AgendaRepository(BaseRepository):
    @staticmethod
    def _conceder_xp(estudante_id, xp_ganho):
        db.session.execute(
            update(Estudante)
            .where(Estudante.id == estudante_id)
            .values(xp_total=func.coalesce(Estudante.xp_total, 0) + xp_ganho)
        )
        pet_id = db.session.execute(
            db.select(Estudante.pet_equipado_id).where(Estudante.id == estudante_id)
        ).scalar_one_or_none()
        if pet_id is not None:
            pet = db.session.execute(
                db.select(Pet).where(Pet.id == pet_id, Pet.estudante_id == estudante_id)
            ).scalar_one_or_none()
            if pet is not None:
                pet.xp_atual = (pet.xp_atual or 0) + xp_ganho
                pet.sincronizar_nivel()

    def listar_atividades(self, estudante_id):
        consulta = (
            db.select(Estudo)
            .join(Agenda, Estudo.agenda_id == Agenda.id)
            .where(Agenda.estudante_id == estudante_id)
            .order_by(Estudo.inicio)
        )
        return db.session.execute(consulta).scalars().all()

    def criar_atividade(
        self, estudante_id, titulo, data, duracao_minutos, lembrete_em=None
    ):
        agenda = db.session.execute(
            db.select(Agenda).where(Agenda.estudante_id == estudante_id)
        ).scalar_one_or_none()
        if agenda is None:
            agenda = Agenda(
                estudante_id=estudante_id,
                data_atual=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.session.add(agenda)
            db.session.flush()
        estudo = Estudo(
            titulo=titulo,
            inicio=datetime.combine(data, datetime.min.time()),
            duracao_minutos=duracao_minutos,
            concluido=False,
            lembrete_em=lembrete_em,
            lembrete_notificado=False,
            agenda_id=agenda.id,
        )
        db.session.add(estudo)
        self.salvar_alteracoes()
        return estudo

    def buscar_atividade_do_estudante(self, estudante_id, estudo_id):
        consulta = (
            db.select(Estudo)
            .join(Agenda, Estudo.agenda_id == Agenda.id)
            .where(Estudo.id == estudo_id, Agenda.estudante_id == estudante_id)
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def listar_lembretes_vencidos(self, estudante_id, agora):
        consulta = (
            db.select(Estudo)
            .join(Agenda, Estudo.agenda_id == Agenda.id)
            .where(
                Agenda.estudante_id == estudante_id,
                Estudo.concluido.is_(False),
                Estudo.lembrete_em.is_not(None),
                Estudo.lembrete_em <= agora,
                Estudo.lembrete_notificado.is_(False),
            )
            .order_by(Estudo.lembrete_em)
        )
        return db.session.execute(consulta).scalars().all()

    def marcar_lembrete_notificado(self, estudante_id, estudo_id, agora):
        resultado = db.session.execute(
            update(Estudo)
            .where(
                Estudo.id == estudo_id,
                Estudo.agenda_id.in_(
                    db.select(Agenda.id).where(Agenda.estudante_id == estudante_id)
                ),
                Estudo.concluido.is_(False),
                Estudo.lembrete_em.is_not(None),
                Estudo.lembrete_em <= agora,
                Estudo.lembrete_notificado.is_(False),
            )
            .values(lembrete_notificado=True)
        )
        if resultado.rowcount != 1:
            self.descartar_alteracoes()
            return False
        self.salvar_alteracoes()
        return True

    def concluir_com_xp(self, estudante_id, estudo_id, xp_ganho):
        resultado = db.session.execute(
            update(Estudo)
            .where(Estudo.id == estudo_id, Estudo.concluido.is_(False))
            .values(concluido=True, xp_ganho=xp_ganho)
        )
        if resultado.rowcount != 1:
            self.descartar_alteracoes()
            return False

        self._conceder_xp(estudante_id, xp_ganho)
        self.salvar_alteracoes()
        return True

    def simular_estudo_concluido(self, estudante_id, duracao_minutos, inicio):
        agenda = db.session.execute(
            db.select(Agenda).where(Agenda.estudante_id == estudante_id)
        ).scalar_one_or_none()
        if agenda is None:
            agenda = Agenda(estudante_id=estudante_id, data_atual=inicio)
            db.session.add(agenda)
            db.session.flush()

        estudo = Estudo(
            titulo="Estudo simulado pelo desenvolvedor",
            inicio=inicio,
            fim=inicio,
            duracao_minutos=duracao_minutos,
            concluido=True,
            agenda_id=agenda.id,
        )
        xp_ganho = calcular_xp_atividade(duracao_minutos)
        estudo.xp_ganho = xp_ganho
        db.session.add(estudo)
        self._conceder_xp(estudante_id, xp_ganho)
        self.salvar_alteracoes()
        return estudo, xp_ganho

    def xp_de_atividades_concluidas(self, estudante_id, inicio, fim):
        return db.session.execute(
            db.select(func.coalesce(func.sum(Estudo.xp_ganho), 0))
            .join(Agenda, Estudo.agenda_id == Agenda.id)
            .where(
                Agenda.estudante_id == estudante_id,
                Estudo.concluido.is_(True),
                Estudo.inicio >= inicio,
                Estudo.inicio < fim,
            )
        ).scalar_one()