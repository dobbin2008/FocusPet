from backend.extensions import db
from backend.models import Estudante, Pet
from backend.repositories.base import BaseRepository


class PetRepository(BaseRepository):
    def listar_disponiveis(self, estudante_id):
        consulta = (
            db.select(Pet)
            .where(Pet.estudante_id == estudante_id)
            .order_by(Pet.id)
        )
        return db.session.execute(consulta).scalars().all()

    def equipar(self, estudante_id, pet_id):
        estudante = db.session.get(Estudante, estudante_id)
        pet = db.session.get(Pet, pet_id)
        if estudante is None or pet is None or pet.estudante_id != estudante_id:
            return None
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

    def resetar_xp_pet_equipado(self, estudante_id):
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
        xp_anterior = pet.xp_atual or 0
        pet.xp_atual = 0
        pet.sincronizar_nivel()
        self.salvar_alteracoes()
        return pet, xp_anterior

    def criar_pets_iniciais_se_necessario(self, estudante_id):
        estudante = db.session.get(Estudante, estudante_id)
        if estudante is None:
            return []
        existentes = db.session.execute(
            db.select(Pet).where(Pet.estudante_id == estudante_id).order_by(Pet.id)
        ).scalars().all()
        existentes_por_linha = {pet.linha_evolutiva: pet for pet in existentes}
        for linha, catalogo in Pet.CATALOGO.items():
            if linha in existentes_por_linha:
                continue
            pet = Pet(
                nome=catalogo["nomes"][0],
                linha_evolutiva=linha,
                nivel=1,
                xp_atual=0,
                eh_padrao=catalogo.get("inicial", False),
                estudante_id=estudante_id,
            )
            db.session.add(pet)
            existentes_por_linha[linha] = pet

        iniciais = [
            existentes_por_linha[linha]
            for linha, catalogo in Pet.CATALOGO.items()
            if catalogo.get("inicial")
        ]
        db.session.flush()
        if estudante.pet_equipado_id is None and iniciais:
            estudante.pet_equipado_id = iniciais[0].id
        self.salvar_alteracoes()
        return iniciais