from sqlalchemy import func, update
from sqlalchemy.orm import selectinload

from backend.extensions import db
from backend.models import BonusMeta, Estudante, Materia, Pet, SessaoFoco
from backend.repositories.base import BaseRepository


class FocusRepository(BaseRepository):
    def buscar_sessao_ativa(self, estudante_id):
        consulta = (
            db.select(SessaoFoco)
            .where(
                SessaoFoco.estudante_id == estudante_id,
                SessaoFoco.modo_ativo.is_(True),
            )
            .order_by(SessaoFoco.id.desc())
        )
        return db.session.execute(consulta).scalars().first()

    def materia_pertence_ao_estudante(self, estudante_id, materia_id):
        consulta = db.select(Materia.id).where(
            Materia.id == materia_id,
            Materia.estudante_id == estudante_id,
        )
        return db.session.execute(consulta).scalar_one_or_none() is not None

    def criar_sessao(self, estudante_id, inicio, token_api, materia_id=None):
        sessao = SessaoFoco(
            estudante_id=estudante_id,
            inicio=inicio,
            token_api=token_api,
            modo_ativo=True,
            vezes_distraido=0,
            materia_id=materia_id,
        )
        db.session.add(sessao)
        self.salvar_alteracoes()
        return sessao

    def buscar_sessao_do_estudante(self, estudante_id, sessao_id):
        consulta = db.select(SessaoFoco).where(
            SessaoFoco.id == sessao_id,
            SessaoFoco.estudante_id == estudante_id,
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def listar_sessoes_concluidas(self, estudante_id, inicio=None, fim_exclusivo=None):
        consulta = db.select(SessaoFoco).where(
            SessaoFoco.estudante_id == estudante_id,
            SessaoFoco.modo_ativo.is_(False),
            SessaoFoco.fim.is_not(None),
        ).options(selectinload(SessaoFoco.materia))
        if inicio is not None:
            consulta = consulta.where(SessaoFoco.inicio >= inicio)
        if fim_exclusivo is not None:
            consulta = consulta.where(SessaoFoco.inicio < fim_exclusivo)
        consulta = consulta.order_by(SessaoFoco.inicio.desc(), SessaoFoco.id.desc())
        return db.session.execute(consulta).scalars().all()

    def buscar_por_token(self, sessao_id, token_api):
        consulta = db.select(SessaoFoco).where(
            SessaoFoco.id == sessao_id,
            SessaoFoco.token_api == token_api,
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def buscar_sessao_concluida(self, estudante_id, sessao_id):
        consulta = db.select(SessaoFoco).where(
            SessaoFoco.id == sessao_id,
            SessaoFoco.estudante_id == estudante_id,
            SessaoFoco.modo_ativo.is_(False),
            SessaoFoco.fim.is_not(None),
        ).options(selectinload(SessaoFoco.materia))
        return db.session.execute(consulta).scalar_one_or_none()

    def encerrar_com_xp(
        self, estudante_id, sessao_id, fim, minutos, xp_ganho, bonus_periodos=None
    ):
        bonus_periodos = bonus_periodos or []
        xp_bonus_meta = sum(bonus["xp_ganho"] for bonus in bonus_periodos)
        resultado = db.session.execute(
            update(SessaoFoco)
            .where(
                SessaoFoco.id == sessao_id,
                SessaoFoco.estudante_id == estudante_id,
                SessaoFoco.modo_ativo.is_(True),
            )
            .values(
                fim=fim,
                modo_ativo=False,
                tempo_total_minutos=minutos,
                xp_ganho=xp_ganho,
                xp_bonus_meta=xp_bonus_meta,
                token_api=None,
            )
        )
        if resultado.rowcount != 1:
            self.descartar_alteracoes()
            return False

        for bonus in bonus_periodos:
            db.session.add(BonusMeta(
                estudante_id=estudante_id,
                tipo=bonus["tipo"],
                periodo_inicio=bonus["periodo_inicio"],
                xp_ganho=bonus["xp_ganho"],
            ))

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
        self.salvar_alteracoes()
        return True

    def registrar_distraicao(self, estudante_id, sessao_id):
        resultado = db.session.execute(
            update(SessaoFoco)
            .where(
                SessaoFoco.id == sessao_id,
                SessaoFoco.estudante_id == estudante_id,
                SessaoFoco.modo_ativo.is_(True),
            )
            .values(vezes_distraido=SessaoFoco.vezes_distraido + 1)
        )
        if resultado.rowcount != 1:
            self.descartar_alteracoes()
            return None
        self.salvar_alteracoes()
        return self.buscar_sessao_do_estudante(estudante_id, sessao_id)