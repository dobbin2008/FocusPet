from datetime import datetime, timezone

from database import DatabaseGateway, get_database, agora, registro


class _FocoSupport:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def _iniciar(self, estudante_id):
        banco = self._db()
        cursor = banco.execute(
            "INSERT INTO sessoes_de_foco (inicio, modo_ativo, vezes_distraido, estudante_id) VALUES (?, 1, 0, ?)",
            (agora(), estudante_id),
        )
        banco.commit()
        return registro(banco.execute("SELECT * FROM sessoes_de_foco WHERE id = ?", (cursor.lastrowid,)).fetchone())

    def _buscar_do_estudante(self, estudante_id, sessao_id):
        sessao = registro(self._db().execute("SELECT * FROM sessoes_de_foco WHERE id = ?", (sessao_id,)).fetchone())
        if not sessao or sessao.estudante_id != estudante_id:
            raise LookupError("Sessão não encontrada")
        return sessao

    def _encerrar(self, estudante_id, sessao_id):
        sessao = self._buscar_do_estudante(estudante_id, sessao_id)
        banco = self._db()
        estudante = banco.execute("SELECT id FROM estudantes WHERE id = ?", (estudante_id,)).fetchone()
        if estudante is None:
            raise LookupError("Estudante não encontrado")
        fim = datetime.now(timezone.utc)
        inicio = datetime.fromisoformat(sessao.inicio)
        minutos = max(0, int((fim - inicio).total_seconds() / 60))
        xp = max(0, minutos * 2 - sessao.vezes_distraido * 5)
        banco.execute("UPDATE sessoes_de_foco SET fim = ?, modo_ativo = 0, tempo_total_minutos = ?, xp_ganho = ? WHERE id = ?", (fim.replace(microsecond=0).isoformat(sep=" "), minutos, xp, sessao_id))
        banco.execute("UPDATE estudantes SET xp_total = COALESCE(xp_total, 0) + ? WHERE id = ?", (xp, estudante_id))
        banco.execute("UPDATE pets SET xp_atual = COALESCE(xp_atual, 0) + ? WHERE estudante_id = ? AND id = (SELECT pet_equipado_id FROM estudantes WHERE id = ?)", (xp, estudante_id, estudante_id))
        banco.commit()
        sessao = self._buscar_do_estudante(estudante_id, sessao_id)
        return sessao

    def _registrar_distraicao(self, estudante_id, sessao_id):
        sessao = self._buscar_do_estudante(estudante_id, sessao_id)
        banco = self._db()
        banco.execute("UPDATE sessoes_de_foco SET vezes_distraido = COALESCE(vezes_distraido, 0) + 1 WHERE id = ?", (sessao_id,))
        banco.commit()
        return self._buscar_do_estudante(estudante_id, sessao_id)


class IniciarModoFocoService(_FocoSupport):
    def execute(self, estudante_id):
        return self._iniciar(estudante_id)


class ConsultarSessaoFocoService(_FocoSupport):
    def execute(self, estudante_id, sessao_id):
        return self._buscar_do_estudante(estudante_id, sessao_id)


class EncerrarModoFocoService(_FocoSupport):
    def execute(self, estudante_id, sessao_id):
        return self._encerrar(estudante_id, sessao_id)


class RegistrarDistracaoService(_FocoSupport):
    def execute(self, estudante_id, sessao_id):
        return self._registrar_distraicao(estudante_id, sessao_id)