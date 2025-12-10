from datetime import datetime, timedelta, time
from typing import Dict, Any, List

from ..llm_client import analyse_message, generate_reply
from ..personas.dina_brows import BASE_PERSONA
from ..domain.sobrancelhas import SERVICOS
from ..schedule.availability import buscar_horarios_livres, calcular_duracao_total, MICRO_BLOCOS
from ..schedule.models import Agendamento


class FlowAgendamentoSobrancelha:
    def __init__(self, repo):
        self.repo = repo

    def _triagem_servico(self, msg: str) -> str:
        lowered = msg.lower()
        if "henna" in lowered:
            return "design_henna"
        if "retoque" in lowered:
            return "retoque_micro"
        if "micro" in lowered:
            return "micro"
        if "avali" in lowered:
            return "avaliacao_sobrancelha"
        if "design" in lowered or "limpar" in lowered or "desenhar" in lowered:
            return "design"
        return ""

    def start(self, state, message: str) -> str:
        state.flow = "agendamento"
        state.step = "identificando_servico"
        servico = self._triagem_servico(message)
        if servico:
            state.data["servico"] = servico
            if servico == "retoque_micro":
                state.step = "checando_regra_especifica"
                return "Quando foi a última micropigmentação? (AAAA-MM-DD)"
            return self._perguntar_data(state)
        return (
            "Claro! Qual o tipo de sobrancelha você deseja? "
            "(só limpar e desenhar / henna / micropigmentação / avaliação)"
        )

    def _perguntar_data(self, state) -> str:
        state.step = "coletando_data"
        return "Qual dia prefere? (formato AAAA-MM-DD)"

    def handle(self, state, message: str, analysis: Dict[str, Any]) -> str:
        if state.step == "identificando_servico":
            servico = self._triagem_servico(message)
            if not servico:
                return (
                    "Pode me dizer se prefere só design, design + henna, micro ou avaliação?"
                )
            state.data["servico"] = servico
            if servico == "retoque_micro":
                state.step = "checando_regra_especifica"
                return "Quando foi a última micropigmentação? (AAAA-MM-DD)"
            return self._perguntar_data(state)

        if state.step == "checando_regra_especifica":
            try:
                last_session = datetime.strptime(message.strip(), "%Y-%m-%d").date()
            except ValueError:
                return "Use o formato AAAA-MM-DD para me dizer a data do último procedimento."
            hoje = datetime.utcnow().date()
            delta = (hoje - last_session).days
            if delta < 30 or delta > 60:
                state.data["servico"] = "avaliacao_sobrancelha"
                state.step = "coletando_data"
                return (
                    "O retoque costuma ser entre 30 e 60 dias. Sugiro uma avaliação primeiro. "
                    "Qual dia prefere marcar a avaliação? (AAAA-MM-DD)"
                )
            state.data["ultima_sessao"] = last_session
            return self._perguntar_data(state)

        if state.step == "coletando_data":
            try:
                data = datetime.strptime(message.strip(), "%Y-%m-%d").date()
            except ValueError:
                return "Use o formato AAAA-MM-DD para o dia, por favor."
            state.data["data"] = data
            state.step = "coletando_horario"
            return "Qual período prefere? manhã/tarde"

        if state.step == "coletando_horario":
            periodo = "manha" if "manh" in message.lower() else "tarde"
            state.data["periodo"] = periodo
            return self._propor_horarios(state)

        if state.step == "aguardando_confirmacao":
            if "sim" in message.lower() or "ok" in message.lower():
                return self._confirmar(state)
            else:
                state.step = "coletando_horario"
                return "Tudo bem, qual outro horário prefere?"

        return "Posso ajudar a marcar seu horário de sobrancelha."

    def _propor_horarios(self, state) -> str:
        servico_id = state.data.get("servico")
        data = state.data.get("data")
        periodo = state.data.get("periodo")
        duracao = calcular_duracao_total([servico_id])
        janela = None
        if servico_id in ["micro", "retoque_micro"]:
            janela = MICRO_BLOCOS
        horarios = buscar_horarios_livres(self.repo, data, duracao, janela=janela)
        if periodo == "manha":
            horarios = [h for h in horarios if int(h.split(":")[0]) < 12]
        elif periodo == "tarde":
            horarios = [h for h in horarios if int(h.split(":")[0]) >= 12]

        if not horarios:
            msg = "Não tenho horários livres nesse período. Posso sugerir outro dia?"
            return generate_reply(BASE_PERSONA, "explicar_indisponibilidade", "neutro", {"mensagem": msg})

        state.data["opcoes"] = horarios[:3]
        state.step = "aguardando_confirmacao"
        return generate_reply(
            BASE_PERSONA,
            "oferecer_opcoes_de_horario",
            "neutro",
            {"opcoes": state.data["opcoes"]},
        )

    def _confirmar(self, state) -> str:
        servico_id = state.data.get("servico")
        data = state.data.get("data")
        horario = state.data.get("opcoes", [None])[0]
        h, m = (horario or "00:00").split(":")
        inicio = time(int(h), int(m))
        duracao = calcular_duracao_total([servico_id])
        fim_dt = datetime.combine(data, inicio) + timedelta(minutes=duracao)
        ag = Agendamento(
            id=0,
            cliente_id=state.data.get("cliente", "anonimo"),
            servico_id=servico_id,
            data=data,
            hora_inicio=inicio,
            hora_fim=fim_dt.time(),
            observacoes=state.data.get("observacoes"),
        )
        self.repo.criar_agendamento(ag)
        state.flow = "idle"
        state.step = "inicio"
        resumo = {
            "data": data.isoformat(),
            "hora": horario,
            "servico": SERVICOS.get(servico_id).nome if SERVICOS.get(servico_id) else servico_id,
        }
        return generate_reply(BASE_PERSONA, "confirmar_agendamento", "positivo", resumo)
