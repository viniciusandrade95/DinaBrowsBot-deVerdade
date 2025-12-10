import os
from typing import Dict, Any
import requests

DEFAULT_BASE_URL = os.getenv("AI_BASE_URL", "https://llm.lab.sspcloud.fr/api")
DEFAULT_MODEL = os.getenv("AI_MODEL", "gpt-oss:120b")
API_KEY = os.getenv("AI_API_KEY", "")


class LLMClientError(RuntimeError):
    pass


def _headers():
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def _call_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not API_KEY:
        # Offline heuristic fallback for tests/dev
        return {"choices": [{"message": {"content": ""}}]}
    url = f"{DEFAULT_BASE_URL}/chat/completions"
    response = requests.post(url, json=payload, headers=_headers(), timeout=30)
    if response.status_code != 200:
        raise LLMClientError(f"LLM call failed: {response.status_code} {response.text}")
    return response.json()


def analyse_message(text: str, conversation_state: Dict[str, Any]) -> Dict[str, Any]:
    lowered = text.lower()
    intent = "small_talk"
    sentimento = "neutro"
    entidades: Dict[str, Any] = {}

    if any(word in lowered for word in ["cancel", "cancelar"]):
        intent = "cancelar"
    elif any(word in lowered for word in ["remarcar", "remarca", "remarcar"]):
        intent = "remarcar"
    elif "me fala" in lowered or "sobre" in lowered:
        intent = "duvida_servico"
    elif any(word in lowered for word in ["agendar", "fazer", "marcar", "sobrancelha", "micro", "henna", "quero"]):
        intent = "agendar_novo"
    elif "duvida" in lowered or "quanto" in lowered or "preco" in lowered:
        intent = "duvida_servico"

    if any(w in lowered for w in ["obrigado", "valeu", "amei"]):
        sentimento = "positivo"
    elif any(w in lowered for w in ["ruim", "pessimo", "triste"]):
        sentimento = "negativo"

    for key in ["design", "henna", "micro", "micropigment", "retoque", "avaliacao"]:
        if key in lowered:
            entidades["servico"] = key
            break

    if "manha" in lowered:
        entidades["periodo"] = "manha"
    elif "tarde" in lowered:
        entidades["periodo"] = "tarde"
    elif "noite" in lowered:
        entidades["periodo"] = "noite"

    result = {"intencao": intent, "sentimento": sentimento, "entidades": entidades}

    if API_KEY:
        prompt = f"Analise a mensagem e retorne JSON com intencao, sentimento e entidades: {text}"
        payload = {"model": DEFAULT_MODEL, "messages": [{"role": "user", "content": prompt}]}
        try:
            _call_llm(payload)
        except LLMClientError:
            pass

    return result


def generate_reply(persona: str, intent: str, sentimento: str, context: Dict[str, Any]) -> str:
    base = persona or ""
    tone = ""
    if sentimento == "positivo":
        tone = "Obrigada pelo carinho! "
    elif sentimento == "negativo":
        tone = "Sinto muito por isso. "

    parts = [base.strip(), tone.strip()]

    if intent == "confirmar_agendamento":
        parts.append(
            f"Confirmei seu horário para {context.get('data')} às {context.get('hora')} para {context.get('servico')}.")
    elif intent == "oferecer_opcoes_de_horario":
        options = context.get("opcoes", [])
        if options:
            parts.append("Tenho estes horários: " + ", ".join(options))
        else:
            parts.append("Não encontrei horários livres, posso sugerir outros dias.")
    elif intent == "explicar_indisponibilidade":
        parts.append(context.get("mensagem", "Esse horário está cheio."))
    else:
        parts.append(context.get("mensagem", "Estou aqui para ajudar com suas sobrancelhas!"))

    reply = " ".join([p for p in parts if p])

    if API_KEY:
        prompt = f"{persona}\nContexto: {context}\nResponda de forma simpática."
        payload = {"model": DEFAULT_MODEL, "messages": [{"role": "user", "content": prompt}]}
        try:
            res = _call_llm(payload)
            content = res.get("choices", [{}])[0].get("message", {}).get("content")
            if content:
                return content
        except LLMClientError:
            pass

    return reply
