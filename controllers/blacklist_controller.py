from flask import Blueprint, jsonify, request, session

from services.blacklist_service import (
    AdicionarSiteBlacklistService,
    ListarBlacklistService,
    ListarUrlsBloqueadasService,
    RemoverSiteBlacklistService,
)

blacklist_bp = Blueprint("blacklist", __name__, url_prefix="")


class BlacklistController:
    def __init__(self, services=None):
        services = services or {}
        self.adicionar = services.get("adicionar", AdicionarSiteBlacklistService())
        self.remover = services.get("remover", RemoverSiteBlacklistService())
        self.listar = services.get("listar", ListarBlacklistService())
        self.urls = services.get("urls", ListarUrlsBloqueadasService())

    def adicionar_site_blacklist(self):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            site = self.adicionar.execute(session["user_id"], request.get_json(silent=True) or {})
            return jsonify({"sucesso": True, "id": site.id, "url": site.url, "descricao": site.descricao,
                            "mensagem": f"Site {site.url} adicionado à lista bloqueada!"}), 201
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500

    def remover_site_blacklist(self, site_id):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            url = self.remover.execute(session["user_id"], site_id)
            return jsonify({"sucesso": True, "mensagem": f"Site {url} removido da lista bloqueada!"}), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500

    def listar_blacklist(self):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            sites = self.listar.execute(session["user_id"])
            return jsonify({"sucesso": True, "sites": [{"id": site.id, "url": site.url, "descricao": site.descricao} for site in sites]}), 200
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500

    def obter_urls_bloqueadas(self):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            return jsonify({"sucesso": True, "urls_bloqueadas": self.urls.execute(session["user_id"])}), 200
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500


blacklist_controller = BlacklistController()
blacklist_bp.add_url_rule("/api/blacklist/adicionar", view_func=blacklist_controller.adicionar_site_blacklist, methods=["POST"])
blacklist_bp.add_url_rule("/api/blacklist/remover/<int:site_id>", view_func=blacklist_controller.remover_site_blacklist, methods=["POST"])
blacklist_bp.add_url_rule("/api/blacklist/listar", view_func=blacklist_controller.listar_blacklist, methods=["GET"])
blacklist_bp.add_url_rule("/api/blacklist/urls", view_func=blacklist_controller.obter_urls_bloqueadas, methods=["GET"])