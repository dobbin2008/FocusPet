from sqlalchemy import func

from backend.extensions import db
from backend.models import Estudante, Pet
from backend.repositories.base import BaseRepository


class DashboardRepository(BaseRepository):
    def buscar_estudante(self, estudante_id):
        return db.session.get(Estudante, estudante_id)

    def buscar_pet_equipado(self, estudante_id):
        consulta = (
            db.select(Pet)
            .join(Estudante, Estudante.pet_equipado_id == Pet.id)
            .where(Estudante.id == estudante_id, Pet.estudante_id == estudante_id)
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def xp_total_dos_pets(self, estudante_id):
        consulta = db.select(func.coalesce(func.sum(Pet.xp_atual), 0)).where(
            Pet.estudante_id == estudante_id
        )
        return db.session.execute(consulta).scalar_one()
