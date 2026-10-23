from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import login_required
from backend.services.blacklist_service import (
    AdicionarSiteBlacklistService,
    ListarBlacklistService,
    ListarUrlsBloqueadasService,
    RemoverSiteBlacklistService,
)

blacklist_bp = Blueprint("blacklist", __name__)


class BlacklistController:
    def __init__(self, services=None):
        services = services or {}
        self.adicionar = services.get("adicionar", AdicionarSiteBlacklistService())
        self.remover = services.get("remover", RemoverSiteBlacklistService())
        self.listar = services.get("listar", ListarBlacklistService())
        self.urls = services.get("urls", ListarUrlsBloqueadasService())

    @login_required
    def adicionar_site_blacklist(self):
        try:
            site = self.adicionar.execute(session["user_id"], request.get_json(silent=True) or {})
            return jsonify({"sucesso": True, "id": site.id, "url": site.url, "descricao": site.descricao}), 201
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400

    @login_required
    def remover_site_blacklist(self, site_id):
        try:
            url = self.remover.execute(session["user_id"], site_id)
            return jsonify({"sucesso": True, "url": url}), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def listar_blacklist(self):
        sites = self.listar.execute(session["user_id"])
        return jsonify({"sucesso": True, "sites": [
            {"id": site.id, "url": site.url, "descricao": site.descricao}
            for site in sites
        ]})

    @login_required
    def obter_urls_bloqueadas(self):
        return jsonify({"sucesso": True, "urls_bloqueadas": self.urls.execute(session["user_id"])})


blacklist_controller = BlacklistController()
blacklist_bp.add_url_rule("/api/blacklist/adicionar", view_func=blacklist_controller.adicionar_site_blacklist, methods=["POST"])
blacklist_bp.add_url_rule("/api/blacklist/remover/<int:site_id>", view_func=blacklist_controller.remover_site_blacklist, methods=["DELETE"])
blacklist_bp.add_url_rule("/api/blacklist/listar", view_func=blacklist_controller.listar_blacklist, methods=["GET"])
blacklist_bp.add_url_rule("/api/blacklist/urls", view_func=blacklist_controller.obter_urls_bloqueadas, methods=["GET"])