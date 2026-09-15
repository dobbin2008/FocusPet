from flask import Blueprint, jsonify, request, session

from services.notas_service import AtualizarNotaService, ExcluirNotaService, ObterNotaService

notas_bp = Blueprint("notas", __name__, url_prefix="")


class NotasController:
    def __init__(self, services=None):
        services = services or {}
        self.obter = services.get("obter", ObterNotaService())
        self.atualizar = services.get("atualizar", AtualizarNotaService())
        self.excluir = services.get("excluir", ExcluirNotaService())

    def bloco_de_notas(self):
        if "user_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        try:
            estudante_id = session["user_id"]
            if request.method == "DELETE":
                self.excluir.execute(estudante_id)
                return jsonify({"sucesso": True, "conteudo": ""}), 200
            nota = self.obter.execute(estudante_id) if request.method == "GET" else self.atualizar.execute(
                estudante_id, request.get_json(silent=True) or {}
            )
            return jsonify({"sucesso": True, "conteudo": nota.conteudo or "", "hotkey": nota.hotkey or "CTRL+Y"}), 200
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        except Exception as erro:
            return jsonify({"erro": str(erro)}), 500


notas_controller = NotasController()
notas_bp.add_url_rule("/api/notas", view_func=notas_controller.bloco_de_notas, methods=["GET", "PUT", "DELETE"])