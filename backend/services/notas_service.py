from backend.models import Nota
from backend.repositories.notas_repository import NotasRepository


def serializar_nota(nota):
    return {"id": nota.id, "titulo": nota.titulo, "conteudo": nota.conteudo or ""}


class ListarNotasService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id):
        return [serializar_nota(nota) for nota in self.repository.listar_do_estudante(estudante_id)]


class CriarNotaService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id, dados):
        titulo = str(dados.get("titulo") or "").strip()
        if not titulo:
            raise ValueError("Informe um nome para a nota.")
        if len(titulo) > 120:
            raise ValueError("O nome da nota deve ter no máximo 120 caracteres.")
        conteudo = dados.get("conteudo", "")
        if not isinstance(conteudo, str):
            raise ValueError("O conteúdo da nota é inválido.")
        return serializar_nota(self.repository.criar(estudante_id, titulo, conteudo))


class ObterNotaService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id, nota_id):
        nota = self.repository.buscar_do_estudante(estudante_id, nota_id)
        if nota is None:
            raise LookupError("Nota não encontrada.")
        return serializar_nota(nota)


class AtualizarNotaService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id, nota_id, dados):
        nota = self.repository.buscar_do_estudante(estudante_id, nota_id)
        if nota is None:
            raise LookupError("Nota não encontrada.")
        if "titulo" in dados:
            titulo = str(dados.get("titulo") or "").strip()
            if not titulo:
                raise ValueError("Informe um nome para a nota.")
            if len(titulo) > 120:
                raise ValueError("O nome da nota deve ter no máximo 120 caracteres.")
            nota.titulo = titulo
        if "conteudo" in dados:
            conteudo = dados["conteudo"]
            if not isinstance(conteudo, str):
                raise ValueError("O conteúdo da nota é inválido.")
            nota.conteudo = conteudo
        return serializar_nota(self.repository.salvar(nota))


class ExcluirNotaService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id, nota_id):
        nota = self.repository.buscar_do_estudante(estudante_id, nota_id)
        if nota is None:
            raise LookupError("Nota não encontrada.")
        self.repository.deletar(nota)


class ObterAtalhoNotaService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id):
        return self.repository.obter_preferencias(estudante_id).hotkey or "CTRL+Y"


class AtualizarAtalhoNotaService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id, atalho):
        hotkey = str(atalho or "").strip().upper()
        if not hotkey or len(hotkey) > 20:
            raise ValueError("Atalho inválido.")
        preferencias = self.repository.obter_preferencias(estudante_id)
        preferencias.hotkey = hotkey
        self.repository.salvar(preferencias)
        return hotkey


class SalvarNotaLegadaService:
    def __init__(self, repository=None):
        self.repository = repository or NotasRepository()

    def execute(self, estudante_id, conteudo):
        if not isinstance(conteudo, str):
            raise ValueError("O conteúdo da nota é inválido.")
        notas = self.repository.listar_do_estudante(estudante_id)
        if notas:
            nota = notas[0]
            nota.conteudo = conteudo
            self.repository.salvar(nota)
        else:
            nota = self.repository.criar(estudante_id, "Minha primeira nota", conteudo)
        return serializar_nota(nota)
