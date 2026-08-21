from models import BlocoDeNotas
from models.database import db


class NotasService:
    def obter(self, estudante_id):
        nota = BlocoDeNotas.obter_ou_criar(estudante_id)
        db.session.commit()
        return nota

    def atualizar(self, estudante_id, dados):
        nota = BlocoDeNotas.obter_ou_criar(estudante_id)
        if "conteudo" in dados:
            nota.editar_anotacao(str(dados["conteudo"]))
        if "hotkey" in dados:
            hotkey = str(dados["hotkey"]).strip().upper()
            if not hotkey or len(hotkey) > 20:
                raise ValueError("Atalho inválido")
            nota.definir_hotkey(hotkey)
        db.session.commit()
        return nota

    def excluir(self, estudante_id):
        nota = BlocoDeNotas.obter_ou_criar(estudante_id)
        nota.excluir_anotacao()
        db.session.commit()