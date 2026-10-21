from backend.extensions import db
from backend.models import Estudante, Pet
from backend.repositories.base import BaseRepository


class PetRepository(BaseRepository):
    def listar_disponiveis(self, estudante_id):
        consulta = (
            db.select(Pet)
            .where(db.or_(Pet.estudante_id.is_(None), Pet.estudante_id == estudante_id))
            .order_by(Pet.id)
        )
        return db.session.execute(consulta).scalars().all()

    def equipar(self, estudante_id, pet_id):
        estudante = db.session.get(Estudante, estudante_id)
        pet = db.session.get(Pet, pet_id)
        if estudante is None or pet is None or pet.estudante_id not in (None, estudante_id):
            return None
        pet.estudante_id = estudante_id
        estudante.pet_equipado_id = pet.id
        self.salvar_alteracoes()
        return pet

    def adicionar_xp_pet_equipado(self, estudante_id, quantidade):
        estudante = db.session.get(Estudante, estudante_id)
        if estudante is None or estudante.pet_equipado_id is None:
            return None
        pet = db.session.execute(
            db.select(Pet).where(
                Pet.id == estudante.pet_equipado_id,
                Pet.estudante_id == estudante_id,
            )
        ).scalar_one_or_none()
        if pet is None:
            return None
        pet.xp_atual = (pet.xp_atual or 0) + quantidade
        pet.sincronizar_nivel()
        self.salvar_alteracoes()
        return pet

    def criar_pets_iniciais_se_necessario(self, estudante_id):
        estudante = db.session.get(Estudante, estudante_id)
        if estudante is None:
            return []
        existentes = db.session.execute(
            db.select(Pet).where(Pet.estudante_id == estudante_id).order_by(Pet.id)
        ).scalars().all()
        if existentes:
            if estudante.pet_equipado_id is None:
                estudante.pet_equipado_id = existentes[0].id
                self.salvar_alteracoes()
            return existentes

        weedle = Pet(
            nome="Weedle",
            linha_evolutiva="grup0",
            nivel=1,
            xp_atual=0,
            eh_padrao=True,
            estudante_id=estudante_id,
        )
        elekid = Pet(
            nome="Elekid",
            linha_evolutiva="grup1",
            nivel=1,
            xp_atual=0,
            eh_padrao=True,
            estudante_id=estudante_id,
        )
        db.session.add_all((weedle, elekid))
        db.session.flush()
        estudante.pet_equipado_id = weedle.id
        self.salvar_alteracoes()
        return [weedle, elekid]