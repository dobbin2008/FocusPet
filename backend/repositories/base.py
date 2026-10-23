from sqlalchemy.exc import SQLAlchemyError

from backend.extensions import db


class BaseRepository:
    def salvar_alteracoes(self):
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def descartar_alteracoes():
        db.session.rollback()