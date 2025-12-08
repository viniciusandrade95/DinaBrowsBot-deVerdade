# bot/router.py
from typing import Optional
import hashlib
import re
from .config import TenantConfig
from .state import SessionState


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_intent(text: str) -> str:
    t = text.lower().strip()
    closing_keywords = ["thanks", "thank you", "bye", "goodbye", "that is all", "that's all", "done", "no more", "appreciate it"]
    if any(word in t for word in closing_keywords):
        return "CLOSING"
    stock_terms = [
        "in stock",
        "stock for",
        "available",
        "availability",
        "do you have",
        "have you got",
    ]
    size_regex = r"\b(?:size\s*\d{1,2}(?:\.\d)?|(?:eu|us)\s*\d{1,2}(?:\.\d)?)\b"
    if any(term in t for term in stock_terms) or re.search(size_regex, t):
        return "STOCK_CHECK"
    if any(w in t for w in ["hour", "open", "close", "opening"]):
        return "STORE_HOURS"
    if any(w in t for w in ["where", "address", "location"]):
        return "STORE_LOCATION"
    if any(w in t for w in ["price", "cost", "how much", "€", "$"]):
        return "PRICE_QUESTION"
    if len(t) < 3:
        return "NOISE"
    return "GENERAL_QUERY"


def decide_model(
    intent: str,
    tenant_config: TenantConfig,
    session: SessionState,
    text: str,
) -> Optional[str]:
    """
    Returns:
      - None -> handle with rules only
      - "20b" -> use gpt-oss:20b
      - "120b" -> use gpt-oss:120b
    """
    if intent == "CLOSING":
        return None
    # Pure rule-based
    if intent in {"STORE_HOURS", "STORE_LOCATION", "STOCK_CHECK"}:
        return None

    # Treat noisy/very short inputs as rule-based so we can ask the user to clarify
    if intent == "NOISE":
        return None

    # Chit-chat disabled → avoid using model if not store-related
    if intent == "GENERAL_QUERY" and not tenant_config.allow_chitchat:
        # You can still call model for store-related reasoning if you want
        # Here we assume general = chit-chat when chitchat is off
        return None

    # Complexity heuristic
    text_len = len(text)
    history_len = session.context.get("history_len", 0)
    cart_value = session.context.get("cart_value", 0)

    # default to tenant preferred model
    default_model = tenant_config.default_model

    # Simple policy:
    high_value = cart_value >= 500
    complex_convo = history_len >= 10 or text_len > 200

    if high_value or complex_convo:
        return "120b"

    # Otherwise use default; if default = 20b this will be cheap for most
    return default_model
