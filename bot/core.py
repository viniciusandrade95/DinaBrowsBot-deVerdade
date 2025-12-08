# bot/core.py
from .config import ConfigStore, TenantConfig
from .state import SessionState, StateStore
from .router import classify_intent, decide_model, hash_text
from .handlers import handle_rule_based
from .models import call_oss_model, has_model_credentials


def handle_message(
    tenant_id: str,
    user_id: str,
    text: str,
    message_id: str,
    state_store: StateStore,
    config_store: ConfigStore,
) -> str:
    text = (text or "").strip()
    if not text:
        return "Por favor, me envie uma mensagem para que eu possa ajudar 😊"

    tenant: TenantConfig = config_store.load_tenant_config(tenant_id)
    session: SessionState = state_store.get_session(tenant_id, user_id)

    tentative_intent = classify_intent(text, session)
    if session.context.get("closed") and tentative_intent != "CLOSING":
        session.reset()
    intent = classify_intent(text, session)

    history_len = session.context.get("history_len", 0)
    session.context["history_len"] = history_len + 1

    if len(text) > 1024:
        return "Mensagem longa demais. Pode resumir um pouco?"

    model_choice = decide_model(intent, tenant, session, text)

    if model_choice is None:
        reply = handle_rule_based(intent, text, tenant, session)
    elif not has_model_credentials():
        reply = handle_rule_based("GENERAL_QUERY", text, tenant, session)
    else:  # pragma: no cover - models not used in rule-first setup
        model_name = f"gpt-oss:{model_choice}"
        try:
            reply = call_oss_model(model_name, tenant, session, text)
        except Exception as exc:  # pragma: no cover
            session.context["last_model_error"] = str(exc)
            reply = (
                "Estou com dificuldade técnica agora, mas posso te ajudar com as informações da DinaBrows."
            )

    if reply.strip().lower() == text.strip().lower():
        reply = (
            "Sou o assistente da DinaBrows. Posso explicar serviços, preços ou marcar um horário."
        )

    session.context["last_question_hash"] = hash_text(text)
    session.touch()
    state_store.save_session(session)

    return reply
