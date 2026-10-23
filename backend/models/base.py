from backend.extensions import db


class CrudModel:
    id = db.Column(db.Integer, primary_key=True)

    def salvar(self):
        db.session.add(self)
        db.session.commit()
        return self

    def atualizar(self, **valores):
        colunas = set(self.__table__.columns.keys()) - {"id"}
        for nome, valor in valores.items():
            if nome in colunas:
                setattr(self, nome, valor)
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def listar_todos(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def buscar_por_id(cls, identificador):
        return db.session.get(cls, identificador)