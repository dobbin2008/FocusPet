from database import DatabaseGateway, get_database, registro


class _BlacklistSupport:
    def __init__(self, database: DatabaseGateway = None):
        self.database = database

    def _db(self):
        return self.database or get_database()

    def _adicionar(self, estudante_id, dados):
        url = str(dados.get("url", "")).strip()
        descricao = dados.get("descricao")
        if not url:
            raise ValueError("URL é obrigatória")
        banco = self._db()
        if banco.execute("SELECT 1 FROM listas_bloqueadas WHERE estudante_id = ? AND url = ?", (estudante_id, url)).fetchone():
            raise ValueError("Este site já está na lista bloqueada")
        cursor = banco.execute(
            "INSERT INTO listas_bloqueadas (url, descricao, estudante_id) VALUES (?, ?, ?)",
            (url, str(descricao).strip() if descricao else None, estudante_id),
        )
        banco.commit()
        return registro(banco.execute("SELECT * FROM listas_bloqueadas WHERE id = ?", (cursor.lastrowid,)).fetchone())

    def _buscar(self, estudante_id, site_id):
        site = registro(self._db().execute("SELECT * FROM listas_bloqueadas WHERE id = ?", (site_id,)).fetchone())
        if not site or site.estudante_id != estudante_id:
            raise LookupError("Site não encontrado")
        return site

    def _remover(self, estudante_id, site_id):
        site = self._buscar(estudante_id, site_id)
        url = site.url
        banco = self._db()
        banco.execute("DELETE FROM listas_bloqueadas WHERE id = ?", (site_id,))
        banco.commit()
        return url

    def _listar(self, estudante_id):
        return [registro(linha) for linha in self._db().execute(
            "SELECT * FROM listas_bloqueadas WHERE estudante_id = ? ORDER BY id", (estudante_id,)
        ).fetchall()]

    def _urls(self, estudante_id):
        return [linha[0] for linha in self._db().execute(
            "SELECT url FROM listas_bloqueadas WHERE estudante_id = ? ORDER BY id", (estudante_id,)
        ).fetchall()]


class AdicionarSiteBlacklistService(_BlacklistSupport):
    def execute(self, estudante_id, dados):
        return self._adicionar(estudante_id, dados)


class RemoverSiteBlacklistService(_BlacklistSupport):
    def execute(self, estudante_id, site_id):
        return self._remover(estudante_id, site_id)


class ListarBlacklistService(_BlacklistSupport):
    def execute(self, estudante_id):
        return self._listar(estudante_id)


class ListarUrlsBloqueadasService(_BlacklistSupport):
    def execute(self, estudante_id):
        return self._urls(estudante_id)