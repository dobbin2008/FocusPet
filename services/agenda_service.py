from datetime import datetime, time

from database import DatabaseGateway, get_database, agora, registro


class _AgendaSupport:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def _agenda_do_estudante(self, estudante_id):
        banco = self._db()
        agenda = banco.execute("SELECT * FROM agendas WHERE estudante_id = ?", (estudante_id,)).fetchone()
        if agenda is None:
            cursor = banco.execute("INSERT INTO agendas (data_atual, estudante_id) VALUES (?, ?)", (agora(), estudante_id))
            banco.commit()
            return registro(banco.execute("SELECT * FROM agendas WHERE id = ?", (cursor.lastrowid,)).fetchone())
        return registro(agenda)

    def _dados_estudo(self, estudo):
        return {
            "id": estudo.id,
            "titulo": estudo.titulo,
            "data": estudo.inicio[:10] if estudo.inicio else None,
            "duracao_minutos": estudo.duracao_minutos or 0,
            "concluido": bool(estudo.concluido),
            "xp": max(10, int((estudo.duracao_minutos or 0) * 1.5)),
        }

    def _listar(self, estudante_id):
        agenda = self._agenda_do_estudante(estudante_id)
        estudos = self._db().execute(
            "SELECT * FROM agenda_atividades WHERE estudante_id = ? ORDER BY inicio", (estudante_id,)
        ).fetchall()
        return [self._dados_estudo(registro(estudo)) for estudo in estudos]

    def _criar(self, estudante_id, data):
        titulo = str(data.get("titulo", "")).strip()
        data_estudo = str(data.get("data", "")).strip()
        if not titulo or not data_estudo:
            raise ValueError("Atividade e data são obrigatórias")
        try:
            data_programada = datetime.strptime(data_estudo, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Data inválida") from exc
        try:
            duracao = max(0, int(data.get("duracao_minutos", 30)))
        except (TypeError, ValueError) as exc:
            raise ValueError("Duração inválida") from exc
        agenda = self._agenda_do_estudante(estudante_id)
        banco = self._db()
        cursor = banco.execute(
            "INSERT INTO estudos (titulo, inicio, duracao_minutos, concluido, agenda_id) VALUES (?, ?, ?, 0, ?)",
            (titulo[:200], data_programada.isoformat() + " 00:00:00", duracao, agenda.id),
        )
        banco.commit()
        return self._dados_estudo(registro(banco.execute("SELECT * FROM estudos WHERE id = ?", (cursor.lastrowid,)).fetchone()))

    def _concluir(self, estudante_id, estudo_id):
        banco = self._db()
        estudo = registro(banco.execute(
            "SELECT estudos.*, agendas.estudante_id FROM estudos JOIN agendas ON agendas.id = estudos.agenda_id WHERE estudos.id = ?",
            (estudo_id,),
        ).fetchone())
        if not estudo or estudo.estudante_id != estudante_id:
            raise LookupError("Atividade não encontrada")
        if estudo.concluido:
            return {"sucesso": True, "xp_ganho": 0, "ja_concluido": True}
        xp_ganho = max(10, int((estudo.duracao_minutos or 0) * 1.5))
        banco.execute("UPDATE estudos SET concluido = 1 WHERE id = ?", (estudo_id,))
        banco.execute("UPDATE estudantes SET xp_total = COALESCE(xp_total, 0) + ? WHERE id = ?", (xp_ganho, estudante_id))
        banco.execute("UPDATE pets SET xp_atual = COALESCE(xp_atual, 0) + ? WHERE estudante_id = ? AND id = (SELECT pet_equipado_id FROM estudantes WHERE id = ?)", (xp_ganho, estudante_id, estudante_id))
        banco.commit()
        estudo.concluido = 1
        return {"sucesso": True, "xp_ganho": xp_ganho, "atividade": self._dados_estudo(estudo)}


class ListarAtividadesService(_AgendaSupport):
    def execute(self, estudante_id):
        return self._listar(estudante_id)


class CriarAtividadeService(_AgendaSupport):
    def execute(self, estudante_id, dados):
        return self._criar(estudante_id, dados)


class ConcluirAtividadeService(_AgendaSupport):
    def execute(self, estudante_id, estudo_id):
        return self._concluir(estudante_id, estudo_id)