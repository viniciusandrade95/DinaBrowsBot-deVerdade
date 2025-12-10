from ..llm_client import generate_reply
from ..personas.dina_brows import BASE_PERSONA


class FlowCancelamento:
    def __init__(self, repo):
        self.repo = repo

    def start(self, state, message: str) -> str:
        state.flow = "cancelamento"
        state.step = "aguardando_id"
        return "Pode me informar o ID do agendamento que deseja cancelar?"

    def handle(self, state, message: str):
        if state.step == "aguardando_id":
            try:
                ag_id = int(message.strip())
            except ValueError:
                return "Envie apenas o número do agendamento, por favor."
            ag = self.repo.cancelar_agendamento(ag_id)
            state.flow = "idle"
            state.step = "inicio"
            if not ag:
                return generate_reply(
                    BASE_PERSONA,
                    "explicar_indisponibilidade",
                    "neutro",
                    {"mensagem": "Não encontrei esse agendamento."},
                )
            return generate_reply(
                BASE_PERSONA,
                "explicar_indisponibilidade",
                "neutro",
                {
                    "mensagem": (
                        f"Agendamento {ag.id} cancelado para {ag.data} às {ag.hora_inicio.strftime('%H:%M')}"
                    )
                },
            )
        return "Posso ajudar a cancelar um horário se quiser."
