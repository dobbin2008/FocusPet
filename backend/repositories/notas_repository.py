from backend.extensions import db
from backend.models import BlocoNotas, Nota
from backend.repositories.base import BaseRepository


class NotasRepository(BaseRepository):
    def listar_do_estudante(self, estudante_id):
        consulta = (
            db.select(Nota)
            .where(Nota.estudante_id == estudante_id)
            .order_by(Nota.id)
        )
        return db.session.execute(consulta).scalars().all()

    def buscar_do_estudante(self, estudante_id, nota_id):
        consulta = db.select(Nota).where(
            Nota.id == nota_id,
            Nota.estudante_id == estudante_id,
        )
        return db.session.execute(consulta).scalar_one_or_none()

    def criar(self, estudante_id, titulo, conteudo=""):
        nota = Nota(estudante_id=estudante_id, titulo=titulo, conteudo=conteudo)
        db.session.add(nota)
        self.salvar_alteracoes()
        return nota

    def salvar(self, nota):
        db.session.add(nota)
        self.salvar_alteracoes()
        return nota

    def deletar(self, nota):
        db.session.delete(nota)
        self.salvar_alteracoes()

    def obter_preferencias(self, estudante_id):
        bloco = BlocoNotas.buscar_por_estudante(estudante_id)
        if bloco is None:
            bloco = BlocoNotas(
                estudante_id=estudante_id,
                conteudo="",
                hotkey="CTRL+Y",
                notas_migradas=True,
            )
            db.session.add(bloco)
            self.salvar_alteracoes()
        return bloco

    def migrar_nota_legada(self, bloco):
        nota = None
        conteudo = (bloco.conteudo or "").strip()
        if conteudo:
            nota = Nota(
                estudante_id=bloco.estudante_id,
                titulo="Minha primeira nota",
                conteudo=bloco.conteudo,
            )
            db.session.add(nota)
        bloco.conteudo = ""
        bloco.notas_migradas = True
        db.session.add(bloco)
        self.salvar_alteracoes()
        return nota
