from backend.extensions import db
from backend.models import ListaBloqueada
from backend.repositories.base import BaseRepository


class BlacklistRepository(BaseRepository):
    def buscar_duplicada(self, estudante_id, url):
        consulta = db.select(ListaBloqueada).where(
            ListaBloqueada.estudante_id == estudante_id,
            ListaBloqueada.url == url,
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def buscar_do_estudante(self, estudante_id, site_id):
        consulta = db.select(ListaBloqueada).where(
            ListaBloqueada.id == site_id,
            ListaBloqueada.estudante_id == estudante_id,
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def listar_sites(self, estudante_id):
        consulta = (
            db.select(ListaBloqueada)
            .where(ListaBloqueada.estudante_id == estudante_id)
            .order_by(ListaBloqueada.id)
        )
        return db.session.execute(consulta).scalars().all()

    def criar_site(self, estudante_id, url, descricao):
        site = ListaBloqueada(estudante_id=estudante_id, url=url, descricao=descricao)
        db.session.add(site)
        self.salvar_alteracoes()
        return site

    def deletar_site(self, site):
        db.session.delete(site)
        self.salvar_alteracoes()