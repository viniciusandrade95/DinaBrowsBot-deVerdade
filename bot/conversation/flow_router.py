from ..llm_client import analyse_message
from .flow_agendamento_sobrancelha import FlowAgendamentoSobrancelha
from .flow_cancelamento import FlowCancelamento


class FlowRouter:
    def __init__(self, repo):
        self.repo = repo
        self.agendamento = FlowAgendamentoSobrancelha(repo)
        self.cancelamento = FlowCancelamento(repo)

    def route(self, state, message: str):
        analysis = analyse_message(message, state.data)
        if state.flow == "agendamento":
            return self.agendamento.handle(state, message, analysis)
        if state.flow == "cancelamento":
            return self.cancelamento.handle(state, message)

        intent = analysis.get("intencao")
        if intent == "cancelar":
            return self.cancelamento.start(state, message)
        if intent == "agendar_novo" and self._is_sobrancelha_related(message):
            return self.agendamento.start(state, message)

        return "Sou a Dina, posso ajudar a marcar ou cancelar sobrancelhas."

    def _is_sobrancelha_related(self, message: str) -> bool:
        lowered = message.lower()
        return any(
            keyword in lowered
            for keyword in ["sobrancelha", "brow", "micro", "henna", "design"]
        )
