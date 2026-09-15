from database import DatabaseGateway, get_database, registro


class _NotasSupport:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def _obter(self, estudante_id):
        return self._obter_ou_criar(estudante_id)

    def _atualizar(self, estudante_id, dados):
        nota = self._obter_ou_criar(estudante_id)
        banco = self._db()
        if "conteudo" in dados:
            nota.conteudo = str(dados["conteudo"])
        if "hotkey" in dados:
            hotkey = str(dados["hotkey"]).strip().upper()
            if not hotkey or len(hotkey) > 20:
                raise ValueError("Atalho inválido")
            nota.hotkey = hotkey
        banco.execute("UPDATE blocos_de_notas SET conteudo = ?, hotkey = ? WHERE id = ?", (nota.conteudo, nota.hotkey, nota.id))
        banco.commit()
        return self._obter_ou_criar(estudante_id)

    def _excluir(self, estudante_id):
        nota = self._obter_ou_criar(estudante_id)
        banco = self._db()
        banco.execute("UPDATE blocos_de_notas SET conteudo = '' WHERE id = ?", (nota.id,))
        banco.commit()

    def _obter_ou_criar(self, estudante_id):
        banco = self._db()
        nota = banco.execute("SELECT * FROM blocos_de_notas WHERE estudante_id = ?", (estudante_id,)).fetchone()
        if nota is None:
            cursor = banco.execute(
                "INSERT INTO blocos_de_notas (conteudo, hotkey, estudante_id) VALUES (?, ?, ?)",
                ("", "CTRL+Y", estudante_id),
            )
            banco.commit()
            nota = banco.execute("SELECT * FROM blocos_de_notas WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return registro(nota)


class ObterNotaService(_NotasSupport):
    def execute(self, estudante_id):
        return self._obter(estudante_id)


class AtualizarNotaService(_NotasSupport):
    def execute(self, estudante_id, dados):
        return self._atualizar(estudante_id, dados)


class ExcluirNotaService(_NotasSupport):
    def execute(self, estudante_id):
        return self._excluir(estudante_id)