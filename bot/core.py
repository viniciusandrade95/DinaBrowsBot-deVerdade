# bot/core.py
from .config import ConfigStore, TenantConfig
from .state import StateStore, SessionState
from .router import classify_intent, decide_model, hash_text
from .handlers import handle_rule_based
from .models import call_oss_model


def handle_message(
    tenant_id: str,
    user_id: str,
    text: str,
    message_id: str,
    state_store: StateStore,
    config_store: ConfigStore,
) -> str:
    """
    Main entrypoint: pure bot logic.
    - Stateless at function level
    - Multi-tenant
    - Routes between rules / 20B / 120B
    """
    text = (text or "").strip()
    if not text:
        return "Please send a message so I can help you 🙂"

    tenant: TenantConfig = config_store.load_tenant_config(tenant_id)
    session: SessionState = state_store.load_state(tenant_id, user_id)

    # Update simple metrics / context
    history_len = session.context.get("history_len", 0)
    session.context["history_len"] = history_len + 1

    # Guardrails – input length, etc.
    if len(text) > 1024:
        return "That message is a bit long. Could you shorten it a little?"

    # Classify intent
    intent = classify_intent(text)

    # Decide if we use rules only, or which model
    model_choice = decide_model(intent, tenant, session, text)

    if model_choice is None:
        reply = handle_rule_based(intent, text, tenant)
    else:
        # model_choice is "20b" or "120b"
        model_name = f"gpt-oss:{model_choice}"
        reply = call_oss_model(model_name, tenant, session, text)

    # Update state for next turn
    session.context["last_question_hash"] = hash_text(text)
    session.last_updated = __import__("time").time()
    state_store.save_state(session)

    return reply
