from datetime import datetime, time

from models import Agenda, Estudante, Estudo
from models.database import db


class AgendaService:
    def _agenda_do_estudante(self, estudante_id):
        agenda = Agenda.query.filter_by(estudante_id=estudante_id).first()
        if agenda is None:
            agenda = Agenda(estudante_id=estudante_id)
            db.session.add(agenda)
            db.session.flush()
        return agenda

    def _dados_estudo(self, estudo):
        return {
            "id": estudo.id,
            "titulo": estudo.titulo,
            "data": estudo.inicio.date().isoformat() if estudo.inicio else None,
            "duracao_minutos": estudo.duracao_minutos or 0,
            "concluido": estudo.concluido,
            "xp": estudo.calcular_xp_para_pet() if estudo.concluido else max(10, int((estudo.duracao_minutos or 0) * 1.5)),
        }

    def listar(self, estudante_id):
        agenda = self._agenda_do_estudante(estudante_id)
        estudos = sorted(agenda.estudos, key=lambda item: item.inicio or datetime.max)
        return [self._dados_estudo(estudo) for estudo in estudos]

    def criar(self, estudante_id, data):
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
        estudo = Estudo(
            titulo=titulo[:200],
            inicio=datetime.combine(data_programada, time.min),
            duracao_minutos=duracao,
            agenda=self._agenda_do_estudante(estudante_id),
        )
        db.session.add(estudo)
        db.session.commit()
        return self._dados_estudo(estudo)

    def concluir(self, estudante_id, estudo_id):
        estudo = Estudo.query.get(estudo_id)
        if not estudo or not estudo.agenda or estudo.agenda.estudante_id != estudante_id:
            raise LookupError("Atividade não encontrada")
        if estudo.concluido:
            return {"sucesso": True, "xp_ganho": 0, "ja_concluido": True}
        estudante = Estudante.query.get(estudante_id)
        estudo.marcar_como_concluido()
        xp_ganho = estudo.calcular_xp_para_pet()
        estudante.adicionar_xp(xp_ganho)
        estudante.ganhar_xp_ao_pet(xp_ganho)
        db.session.commit()
        return {"sucesso": True, "xp_ganho": xp_ganho, "atividade": self._dados_estudo(estudo)}