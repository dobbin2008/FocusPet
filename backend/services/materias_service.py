from backend.models import Materia
from backend.repositories.materias_repository import MateriasRepository


def _dados_materia(materia, minutos):
    return {
        "id": materia.id,
        "nome": materia.nome,
        "minutos_estudados_semana": minutos,
        "horas_estudadas_semana": round(minutos / 60, 2),
    }


class ListarMateriasService:
    def __init__(self, repository=None):
        self.repository = repository or MateriasRepository()

    def execute(self, estudante_id):
        materias = self.repository.listar_do_estudante(estudante_id)
        minutos = self.repository.minutos_estudados_esta_semana(estudante_id)
        return [_dados_materia(materia, minutos.get(materia.id, 0)) for materia in materias]


class CadastrarMateriaService:
    def __init__(self, repository=None):
        self.repository = repository or MateriasRepository()

    def execute(self, estudante_id, dados):
        nome = str((dados or {}).get("nome", "")).strip()
        if not nome:
            raise ValueError("Informe o nome da matéria.")
        if len(nome) > 80:
            raise ValueError("O nome da matéria deve ter no máximo 80 caracteres.")
        if self.repository.nome_em_uso(estudante_id, nome):
            raise ValueError("Você já cadastrou uma matéria com esse nome.")

        materia = Materia(nome=nome, estudante_id=estudante_id).salvar()
        return _dados_materia(materia, 0)


class EditarMateriaService:
    def __init__(self, repository=None):
        self.repository = repository or MateriasRepository()

    def execute(self, estudante_id, materia_id, dados):
        nome = str((dados or {}).get("nome", "")).strip()
        if not nome:
            raise ValueError("Informe o nome da matéria.")
        if len(nome) > 80:
            raise ValueError("O nome da matéria deve ter no máximo 80 caracteres.")

        materia = self.repository.buscar_do_estudante(estudante_id, materia_id)
        if materia is None:
            raise LookupError("Matéria não encontrada.")
        if self.repository.nome_em_uso(estudante_id, nome, excluir_id=materia_id):
            raise ValueError("Você já cadastrou uma matéria com esse nome.")

        materia.atualizar(nome=nome)
        minutos = self.repository.minutos_estudados_esta_semana(estudante_id)
        return _dados_materia(materia, minutos.get(materia.id, 0))
