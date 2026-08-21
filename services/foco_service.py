from models import Estudante, SessaoFoco
from models.database import db


class FocoService:
    def iniciar(self, estudante_id):
        sessao = SessaoFoco(estudante_id=estudante_id)
        sessao.iniciar_modo_foco()
        db.session.add(sessao)
        db.session.commit()
        return sessao

    def buscar_do_estudante(self, estudante_id, sessao_id):
        sessao = SessaoFoco.query.get(sessao_id)
        if not sessao or sessao.estudante_id != estudante_id:
            raise LookupError("Sessão não encontrada")
        return sessao

    def encerrar(self, estudante_id, sessao_id):
        sessao = self.buscar_do_estudante(estudante_id, sessao_id)
        estudante = Estudante.query.get(estudante_id)
        if estudante is None:
            raise LookupError("Estudante não encontrado")
        sessao.desativar_modo_foco()
        db.session.commit()
        estudante.adicionar_xp(sessao.xp_ganho)
        estudante.ganhar_xp_ao_pet(sessao.xp_ganho)
        db.session.commit()
        return sessao

    def registrar_distraicao(self, estudante_id, sessao_id):
        sessao = self.buscar_do_estudante(estudante_id, sessao_id)
        sessao.registrar_distraicao()
        db.session.commit()
        return sessao