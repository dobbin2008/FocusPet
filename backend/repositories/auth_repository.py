from backend.extensions import db
from backend.models import Estudante
from backend.repositories.base import BaseRepository


class AuthRepository(BaseRepository):
    def buscar_por_email(self, email):
        return db.session.execute(
            db.select(Estudante).where(Estudante.email == email)
        ).scalar_one_or_none()