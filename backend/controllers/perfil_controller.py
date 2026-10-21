from flask import Blueprint, current_app, jsonify, request, send_file, session
from werkzeug.exceptions import RequestEntityTooLarge

from backend.controllers.auth_controller import login_required, pagina_estatica
from backend.services.perfil_service import (
    AtualizarPerfilService,
    ObterFotoPerfilService,
    ObterPerfilService,
)

perfil_bp = Blueprint("perfil", __name__)


@perfil_bp.errorhandler(RequestEntityTooLarge)
def upload_muito_grande(_erro):
    return jsonify({"erro": "A imagem deve ter no máximo 5 MB"}), 413


class PerfilController:
    def __init__(self, obter_foto_service=None, obter_perfil_service=None, atualizar_perfil_service=None):
        self.obter_foto = obter_foto_service or ObterFotoPerfilService()
        self.obter_perfil = obter_perfil_service or ObterPerfilService()
        self.atualizar_perfil = atualizar_perfil_service or AtualizarPerfilService()

    @login_required
    def pagina(self):
        return pagina_estatica("perfil.html")

    @login_required
    def api_perfil(self):
        try:
            if request.method == "GET":
                return jsonify({"sucesso": True, **self.obter_perfil.execute(session["user_id"])})
            dados = request.form
            perfil = self.atualizar_perfil.execute(
                session["user_id"],
                dados.get("nome"),
                request.files.get("foto_perfil"),
                dados.get("remover_foto") == "true",
                current_app.config["PROFILE_UPLOAD_FOLDER"],
            )
            return jsonify({"sucesso": True, **perfil})
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @login_required
    def foto(self):
        caminho = self.obter_foto.execute(
            session["user_id"], current_app.config["PROFILE_UPLOAD_FOLDER"]
        )
        if caminho is None:
            return jsonify({"erro": "Foto de perfil não encontrada"}), 404
        return send_file(caminho, mimetype="image/webp", conditional=True, max_age=0)


perfil_controller = PerfilController()
perfil_bp.add_url_rule("/perfil", view_func=perfil_controller.pagina, methods=["GET"])
perfil_bp.add_url_rule("/api/perfil", view_func=perfil_controller.api_perfil, methods=["GET", "PATCH"])
perfil_bp.add_url_rule("/api/perfil/foto", view_func=perfil_controller.foto, methods=["GET"])