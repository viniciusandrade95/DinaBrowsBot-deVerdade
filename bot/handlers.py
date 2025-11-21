# bot/handlers.py
from .config import TenantConfig


def handle_rule_based(intent: str, text: str, tenant: TenantConfig) -> str:
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

    if intent == "NOISE":
        return "I didn’t quite catch that. Could you rephrase your question?"

    # Fallback for when model is disabled / no routing
    if not tenant.allow_chitchat:
        return (
            "I can help with store information, product details, stock and prices. "
            "What would you like to know?"
        )

    # Generic fallback – this will normally be used only if routing chose no model
    return "What would you like to know about our products or store? 🙂"
