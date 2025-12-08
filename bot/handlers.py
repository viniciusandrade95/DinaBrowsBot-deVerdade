# bot/handlers.py
from typing import Optional

from .config import TenantConfig
from .state import SessionState


def _rotate_suggestion(session: Optional[SessionState]) -> str:
    """Cycle through quick prompts so the bot doesn't repeat itself."""

    options = [
        "Need help finding a specific model or size?",
        "I can check color options or suggest similar styles.",
        "If you want, share your size and what you're looking for and I'll shortlist picks.",
    ]

    if session is None:
        return options[0]

    idx = session.context.get("suggestion_idx", 0) % len(options)
    session.context["suggestion_idx"] = idx + 1
    return options[idx]


def _general_query_reply(
    text: str, tenant: TenantConfig, session: Optional[SessionState]
) -> str:
    tone = tenant.tone
    info = tenant.store_info
    lower = text.lower()

    if any(greet in lower for greet in ["hi", "hello", "hey", "olá", "oi"]):
        opener = "Hi" if tone != "playful" else "Hey"
        return (
            f"{opener}! You're chatting with {tenant.name}. "
            f"We’re at {info.get('address', 'our main store')} and open {info.get('openingHours', 'today')}. "
            f"What sneakers or accessories are you looking for?"
        )

    if any(word in lower for word in ["return", "exchange", "refund"]):
        return (
            "We offer returns and exchanges within 30 days if items are unused and boxed. "
            "Bring your receipt or order number and I'll sort it out."
        )

    if any(word in lower for word in ["deliver", "shipping", "ship", "pickup", "collection"]):
        return (
            "We can arrange in-store pickup or courier delivery. "
            f"Tell me your city and the product you want and I'll confirm options."
        )

    if any(word in lower for word in ["stock", "available", "availability", "size"]):
        return (
            "I can check stock for you. Share the product name and size (EU/US), "
            "and I'll confirm availability."
        )

    # Provide a more helpful generic reply with rotating suggestions
    suggestion = _rotate_suggestion(session)
    return (
        "I can help with sneakers, accessories, and order updates. "
        f"Tell me the model or style you're after and your size. {suggestion}"
    )


def handle_rule_based(
    intent: str, text: str, tenant: TenantConfig, session: Optional[SessionState] = None
) -> str:
    tone = tenant.tone
    info = tenant.store_info

    if intent == "STORE_HOURS":
        if tone == "friendly":
            return f"We’re usually open {info.get('openingHours', 'during business hours')} 😊"
        elif tone == "playful":
            return f"We open {info.get('openingHours', 'most days')} – come say hi! 🎉"
        else:
            return f"Our opening hours are: {info.get('openingHours', 'standard business hours')}."

    if intent == "STORE_LOCATION":
        if tone == "friendly":
            return f"You’ll find us at {info.get('address', 'our main store')} 📍"
        elif tone == "playful":
            return f"We’re at {info.get('address', 'our secret HQ')} – don’t get lost 👀"
        else:
            return f"Our address is: {info.get('address', 'not specified')}."

    if intent == "PRICE_QUESTION":
        # Here you’d plug in product search / catalog lookup
        return (
            "I can help with prices – tell me the product name, model, or share a photo and "
            "I’ll look it up for you."
        )

    if intent == "CLOSING":
        if session is not None:
            session.flow = "CLOSED"
            session.step = "END"
            session.context["closed"] = True
        return (
            f"Thanks for chatting with {tenant.name}! "
            "I’ve noted your request. If you need anything else later, just send a new message."
        )

    if intent == "NOISE":
        return "I didn’t quite catch that. Could you rephrase your question?"

    # Fallback for when model is disabled / no routing
    if not tenant.allow_chitchat:
        return _general_query_reply(text, tenant, session)

    # Generic fallback – this will normally be used only if routing chose no model
    return _general_query_reply(text, tenant, session)
