from functools import wraps

from flask import Blueprint, jsonify, request, session

from backend.controllers.auth_controller import login_required
from backend.services.foco_service import (
    ConsultarSessaoFocoService,
    EncerrarModoFocoService,
    IniciarModoFocoService,
    ObterSessaoFocoAtivaService,
    RegistrarDistracaoService,
    ValidarTokenSessaoService,
)

foco_bp = Blueprint("foco", __name__)


def sessao_foco_autenticada(view_func):
    @wraps(view_func)
    def decorator(self, sessao_id, *args, **kwargs):
        estudante_id = session.get("user_id")
        if estudante_id is None:
            esquema, _, token_api = request.headers.get("Authorization", "").partition(" ")
            if esquema.lower() != "bearer":
                return jsonify({"erro": "Não autenticado"}), 401
            sessao = self.validar_token.execute(sessao_id, token_api)
            if sessao is None:
                return jsonify({"erro": "Token de sessão inválido ou expirado"}), 401
            estudante_id = sessao.estudante_id
        kwargs["estudante_id"] = estudante_id
        return view_func(self, sessao_id, *args, **kwargs)

    return decorator


class FocoController:
    def __init__(self, services=None):
        services = services or {}
        self.iniciar = services.get("iniciar", IniciarModoFocoService())
        self.obter_ativa = services.get("obter_ativa", ObterSessaoFocoAtivaService())
        self.encerrar = services.get("encerrar", EncerrarModoFocoService())
        self.consultar = services.get("consultar", ConsultarSessaoFocoService())
        self.distracao = services.get("distracao", RegistrarDistracaoService())
        self.validar_token = services.get("validar_token", ValidarTokenSessaoService())

    @login_required
    def iniciar_modo_foco(self):
        dados = request.get_json(silent=True) or {}
        if not isinstance(dados, dict):
            return jsonify({"erro": "Dados da sessão inválidos."}), 400
        try:
            materia_id = dados.get("materia_id")
            if materia_id in ("", None):
                materia_id = None
            else:
                if isinstance(materia_id, bool):
                    raise ValueError
                if isinstance(materia_id, str) and not materia_id.isdecimal():
                    raise ValueError
                if not isinstance(materia_id, (int, str)):
                    raise ValueError
                materia_id = int(materia_id)
                if materia_id <= 0:
                    raise ValueError
        except (TypeError, ValueError):
            return jsonify({"erro": "Matéria inválida."}), 400
        try:
            sessao, criada = self.iniciar.execute(session["user_id"], materia_id)
        except ValueError as erro:
            return jsonify({"erro": str(erro)}), 400
        return jsonify({
            "sucesso": True,
            "sessao_id": sessao.id,
            "token_api": sessao.token_api,
            "inicio": sessao.inicio.isoformat(),
            "vezes_distraido": sessao.vezes_distraido or 0,
            "materia_id": sessao.materia_id,
            "materia_nome": sessao.materia.nome if sessao.materia else None,
            "ja_ativa": not criada,
            "mensagem": "Modo foco iniciado!",
        }), 201 if criada else 200

    @login_required
    def obter_sessao_ativa(self):
        sessao = self.obter_ativa.execute(session["user_id"])
        if sessao is None:
            return jsonify({"sucesso": True, "sessao": None})
        return jsonify({
            "sucesso": True,
            "sessao": {
                "sessao_id": sessao.id,
                "token_api": sessao.token_api,
                "inicio": sessao.inicio.isoformat(),
                "vezes_distraido": sessao.vezes_distraido or 0,
                "materia_id": sessao.materia_id,
                "materia_nome": sessao.materia.nome if sessao.materia else None,
            },
        })

    @sessao_foco_autenticada
    def encerrar_modo_foco(self, sessao_id, estudante_id):
        try:
            sessao = self.encerrar.execute(estudante_id, sessao_id)
            return jsonify({
                "sucesso": True,
                "tempo_minutos": sessao.tempo_total_minutos,
                "vezes_distraido": sessao.vezes_distraido,
                "xp_ganho": sessao.xp_ganho,
                "xp_bonus_meta": sessao.xp_bonus_meta or 0,
                "xp_base": max(0, (sessao.xp_ganho or 0) - (sessao.xp_bonus_meta or 0)),
                "ja_concluida": sessao.ja_concluida,
                "mensagem": "Sessão já encerrada." if sessao.ja_concluida else "Sessão finalizada!",
            }), 200
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @sessao_foco_autenticada
    def obter_status_sessao(self, sessao_id, estudante_id):
        try:
            sessao = self.consultar.execute(estudante_id, sessao_id)
            return jsonify({
                "sucesso": True,
                "sessao_id": sessao.id,
                "modo_ativo": bool(sessao.modo_ativo),
                "tempo_total_minutos": sessao.minutos_estudados,
                "tempo_total_segundos": sessao.segundos_estudados,
                "vezes_distraido": sessao.vezes_distraido,
                "inicio": sessao.inicio.isoformat() if sessao.inicio else None,
                "fim": sessao.fim.isoformat() if sessao.fim else None,
                "xp_ganho": sessao.xp_ganho,
            })
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404

    @sessao_foco_autenticada
    def registrar_distracao(self, sessao_id, estudante_id):
        try:
            sessao = self.distracao.execute(estudante_id, sessao_id)
            return jsonify({"sucesso": True, "vezes_distraido": sessao.vezes_distraido})
        except LookupError as erro:
            return jsonify({"erro": str(erro)}), 404


foco_controller = FocoController()
foco_bp.add_url_rule("/api/foco/iniciar", view_func=foco_controller.iniciar_modo_foco, methods=["POST"])
foco_bp.add_url_rule("/api/foco/ativa", view_func=foco_controller.obter_sessao_ativa, methods=["GET"])
foco_bp.add_url_rule("/api/foco/encerrar/<int:sessao_id>", view_func=foco_controller.encerrar_modo_foco, methods=["POST"])
foco_bp.add_url_rule("/api/foco/status/<int:sessao_id>", view_func=foco_controller.obter_status_sessao, methods=["GET"])
foco_bp.add_url_rule("/api/foco/registrar-distracao/<int:sessao_id>", view_func=foco_controller.registrar_distracao, methods=["POST"])