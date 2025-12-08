# bot/router.py
from typing import Optional
import hashlib

from .config import TenantConfig
from .state import SessionState


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_intent(text: str, session: Optional[SessionState] = None) -> str:
    t = text.lower().strip()
    if session and session.context.get("booking"):
        return "BOOKING_FLOW"

    closing_keywords = ["obrigado", "obrigada", "vlw", "tchau", "até", "ate", "bye", "thanks"]
    if any(word in t for word in closing_keywords):
        return "CLOSING"

    if any(k in t for k in ["onde fica", "endereco", "endereço", "local", "localizacao", "localização", "morada"]):
        return "STORE_LOCATION"

    if any(k in t for k in ["horario", "horário", "abre", "fecha", "funciona", "funcionam"]):
        return "STORE_HOURS"

    if any(k in t for k in ["nao sei", "não sei", "qual serviço", "qual servico", "o que recomenda", "melhor opção"]):
        return "SERVICE_ADVICE"

    if any(k in t for k in ["serviço", "servicos", "serviços", "preço", "preços", "valores", "tabela"]):
        return "LIST_SERVICES"

    if any(k in t for k in ["agendar", "marcar", "marcação", "marcacao", "agendamento", "quero um horário", "quero horario"]):
        return "BOOKING_START"

    # service detail heuristic: mention of known keywords
    brow_terms = ["lamination", "sobrancelha", "sobrancelhas", "design", "manutenção", "manutencao"]
    if any(term in t for term in brow_terms):
        return "SERVICE_DETAIL"

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
    # DinaBrows bot is fully rule-based for now
    return None
