"""Simple booking flow helpers for DinaBrows."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from .state import SessionState
from .knowledge import find_service_by_name_or_keyword, list_services

BOOKING_FILE = Path("data/bookings.json")


def _init_booking_context(session: SessionState) -> Dict:
    booking = session.context.get("booking") or {
        "step": "ask_service",
        "data": {
            "service_id": None,
            "date": None,
            "time": None,
            "name": None,
            "phone": None,
        },
    }
    session.context["booking"] = booking
    session.flow = "BOOKING"
    session.step = booking.get("step", "ask_service")
    return booking


def start_booking(session: SessionState) -> str:
    booking = _init_booking_context(session)
    return (
        "Perfeito, vamos agendar na DinaBrows. Qual serviço de sobrancelhas você quer? "
        "Posso marcar Brow Lamination, Design de Sobrancelhas ou Manutenção."
    )


def _save_booking_record(record: Dict) -> None:
    BOOKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if BOOKING_FILE.exists():
        try:
            existing = json.loads(BOOKING_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []
    existing.append(record)
    BOOKING_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def _format_service(service_id: str) -> Optional[str]:
    for service in list_services():
        if service.get("id") == service_id:
            return f"{service['name']} (R$ {service['price_brl']}, {service['duration_minutes']} min)"
    return None


def handle_booking_reply(session: SessionState, text: str) -> str:
    booking = _init_booking_context(session)
    data = booking["data"]

    if booking["step"] == "ask_service":
        service = find_service_by_name_or_keyword(text)
        if service:
            data["service_id"] = service["id"]
            booking["step"] = "ask_date"
            session.step = "ask_date"
            return (
                f"Ótima escolha: {service['name']} (R$ {service['price_brl']}, {service['duration_minutes']} min). "
                "Qual data você prefere? (ex: 10/06)"
            )
        return "Qual serviço você gostaria de agendar? Temos Brow Lamination, Design ou Manutenção."

    if booking["step"] == "ask_date":
        if text.strip():
            data["date"] = text.strip()
            booking["step"] = "ask_time"
            session.step = "ask_time"
            return "Anotado! Qual horário fica melhor pra você? (ex: 15:00)"
        return "Pode me informar a data desejada?"

    if booking["step"] == "ask_time":
        if text.strip():
            data["time"] = text.strip()
            booking["step"] = "ask_name"
            session.step = "ask_name"
            return "Seu nome para a reserva?"
        return "Qual horário prefere?"

    if booking["step"] == "ask_name":
        if text.strip():
            data["name"] = text.strip()
            booking["step"] = "ask_phone"
            session.step = "ask_phone"
            return "E o seu telefone/WhatsApp para contato?"
        return "Como posso chamar você para confirmar?"

    if booking["step"] == "ask_phone":
        if text.strip():
            data["phone"] = text.strip()
            booking["step"] = "confirm"
            session.step = "confirm"

    if booking["step"] == "confirm":
        service_label = _format_service(data.get("service_id")) or "Serviço"
        record = {
            "tenant": session.tenant_id,
            "user": session.user_id,
            **data,
        }
        _save_booking_record(record)
        session.flow = "IDLE"
        session.step = "NONE"
        session.context.pop("booking", None)
        return (
            f"Agendamento registrado! {service_label} em {data.get('date')} às {data.get('time')} para {data.get('name')}"
            f" (contato: {data.get('phone')}). Se precisar ajustar algo, é só avisar."
        )

    return "Vou te ajudar a marcar. Qual serviço você quer reservar?"
