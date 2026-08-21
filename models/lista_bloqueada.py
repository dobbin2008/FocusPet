from .database import db


class ListaBloqueada(db.Model):
    __tablename__ = "listas_bloqueadas"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    estudante_id = db.Column(db.Integer, db.ForeignKey("estudantes.id"), nullable=False)

    estudante = db.relationship("Estudante", back_populates="lista_bloqueada")

    @classmethod
    def adicionar_site(cls, estudante_id: int, url: str, descricao: str = None) -> "ListaBloqueada":
        """Adiciona um site à lista bloqueada."""
        if not url or not url.strip():
            raise ValueError("URL é obrigatória")

        # Verificar se o site já está na lista
        site_existente = cls.query.filter_by(
            estudante_id=estudante_id, url=url.strip()
        ).first()
        if site_existente:
            raise ValueError("Este site já está na lista bloqueada")

        site = cls(
            url=url.strip(),
            descricao=descricao.strip() if descricao else None,
            estudante_id=estudante_id
        )
        db.session.add(site)
        db.session.commit()
        return site

    @classmethod
    def remover_site(cls, site_id: int) -> bool:
        """Remove um site da lista bloqueada."""
        site = cls.query.get(site_id)
        if site:
            db.session.delete(site)
            db.session.commit()
            return True
        return False

    @classmethod
    def listar_por_estudante(cls, estudante_id: int):
        """Lista todos os sites bloqueados de um estudante."""
        return cls.query.filter_by(estudante_id=estudante_id).all()

    @classmethod
    def obter_urls_por_estudante(cls, estudante_id: int) -> list:
        """Retorna apenas as URLs como lista, útil para enviar à extensão."""
        sites = cls.query.filter_by(estudante_id=estudante_id).all()
        return [site.url for site in sites]
