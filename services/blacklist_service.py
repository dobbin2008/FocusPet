from models import ListaBloqueada


class BlacklistService:
    def adicionar(self, estudante_id, dados):
        return ListaBloqueada.adicionar_site(
            estudante_id=estudante_id,
            url=dados.get("url", ""),
            descricao=dados.get("descricao"),
        )

    def buscar(self, estudante_id, site_id):
        site = ListaBloqueada.query.get(site_id)
        if not site or site.estudante_id != estudante_id:
            raise LookupError("Site não encontrado")
        return site

    def remover(self, estudante_id, site_id):
        site = self.buscar(estudante_id, site_id)
        url = site.url
        ListaBloqueada.remover_site(site_id)
        return url

    def listar(self, estudante_id):
        return ListaBloqueada.listar_por_estudante(estudante_id)

    def urls(self, estudante_id):
        return ListaBloqueada.obter_urls_por_estudante(estudante_id)