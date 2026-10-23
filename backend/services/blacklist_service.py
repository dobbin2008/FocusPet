from urllib.parse import urlsplit

from backend.repositories.blacklist_repository import BlacklistRepository


class AdicionarSiteBlacklistService:
    def __init__(self, repository=None):
        self.repository = repository or BlacklistRepository()

    def execute(self, estudante_id, dados):
        url = str(dados.get("url", "")).strip()
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Informe uma URL http ou https válida")
        url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        if self.repository.buscar_duplicada(estudante_id, url):
            raise ValueError("Este site já está na lista bloqueada")
        descricao = str(dados.get("descricao") or "").strip()[:255] or None
        return self.repository.criar_site(estudante_id, url, descricao)


class RemoverSiteBlacklistService:
    def __init__(self, repository=None):
        self.repository = repository or BlacklistRepository()

    def execute(self, estudante_id, site_id):
        site = self.repository.buscar_do_estudante(estudante_id, site_id)
        if site is None:
            raise LookupError("Site não encontrado")
        url = site.url
        self.repository.deletar_site(site)
        return url


class ListarBlacklistService:
    def __init__(self, repository=None):
        self.repository = repository or BlacklistRepository()

    def execute(self, estudante_id):
        return self.repository.listar_sites(estudante_id)


class ListarUrlsBloqueadasService:
    def __init__(self, repository=None):
        self.repository = repository or BlacklistRepository()

    def execute(self, estudante_id):
        return [site.url for site in self.repository.listar_sites(estudante_id)]