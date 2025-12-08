# bot/handlers.py
from __future__ import annotations

from typing import Optional

from .config import TenantConfig
from .state import SessionState
from .knowledge import get_studio_info, list_services, find_service_by_name_or_keyword
from .booking import handle_booking_reply, start_booking



def _greeting() -> str:
    info = get_studio_info()
    return (
        "Oi! Eu sou o assistente da DinaBrows 😊 Como posso te ajudar hoje? "
        "Posso explicar serviços, valores ou marcar um horário para você."
        f" Estamos na {info['address']}."
    )


def _format_services_list() -> str:
    services = list_services()
    lines = [
        "Aqui estão os serviços da DinaBrows:",
    ]
    for service in services:
        lines.append(
            f"- {service['name']}: R$ {service['price_brl']} | {service['duration_minutes']} min"
        )
    lines.append("Quer saber detalhes ou já quer agendar algum?")
    return "\n".join(lines)


def _service_details(text: str) -> Optional[str]:
    service = find_service_by_name_or_keyword(text)
    if not service:
        return None
    return (
        f"{service['name']}: {service['description']} "
        f"Duração: {service['duration_minutes']} min. Preço: R$ {service['price_brl']}."
    )


def handle_rule_based(
    intent: str, text: str, tenant: TenantConfig, session: Optional[SessionState] = None
) -> str:
    # Booking flow has priority
    if session and session.context.get("booking") and intent != "CLOSING":
        return handle_booking_reply(session, text)

    info = get_studio_info()

    if intent == "BOOKING_START":
        return start_booking(session) if session else "Vamos agendar! Me fale seu nome."  # pragma: no cover

    if intent == "BOOKING_FLOW":
        return handle_booking_reply(session, text)

    if intent == "CLOSING":
        if session is not None:
            session.flow = "CLOSED"
            session.step = "END"
            session.context["closed"] = True
        return "Obrigada por falar com a DinaBrows! Qualquer coisa é só chamar de novo."

    if intent == "STORE_LOCATION":
        return f"Estamos na {info['address']}."

    if intent == "STORE_HOURS":
        return f"Funcionamos: {info['openingHours']}. Quer que eu veja um horário pra você?"

    if intent == "LIST_SERVICES":
        return _format_services_list()

    if intent == "SERVICE_DETAIL":
        detail = _service_details(text)
        if detail:
            return detail + " Quer agendar?"
        return "Fazemos Brow Lamination, Design e Manutenção de sobrancelhas. Qual deles você quer saber mais?"

    if intent == "SERVICE_ADVICE":
        return (
            "Me conta: você prefere um resultado mais natural ou bem definido? "
            "Se nunca fez brow lamination, posso sugerir o Design de Sobrancelhas para começar."
        )

    if intent == "NOISE":
        return "Não entendi bem. Pode me dizer o que você precisa sobre sobrancelhas ou agendamento?"

    # GENERAL_QUERY or fallback
    lower = text.lower()
    if any(greet in lower for greet in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        return _greeting()

    return (
        "Sou o assistente da DinaBrows. Posso passar endereço, horários, explicar serviços de sobrancelhas "
        "ou marcar um horário. O que você gostaria?"
    )
