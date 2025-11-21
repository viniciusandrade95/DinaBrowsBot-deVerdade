# bot/models.py
import requests
from typing import List, Dict
from .config import TenantConfig
from .state import SessionState

# --- Configuration ---
API_KEY = "sk-97b27b041cc0446e99a4ee2a0f85ab60"   # ⚠️ Replace with your real key or load from env
BASE_URL = "https://llm.lab.sspcloud.fr/api"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}


def build_system_prompt(tenant: TenantConfig) -> str:
    """
    Builds the system prompt with tone, language, store info and constraints.
    """
    return (
        f"You are a {tenant.tone} sales assistant for the store '{tenant.name}'. "
        f"Always answer in {tenant.language}. "
        f"Use the {tenant.currency} currency for amounts. "
        "Focus ONLY on questions related to this store, its products, orders and policies. "
        "If the user asks something unrelated, gently redirect them. "
        "Never invent product data or prices. "
        "If unsure, say so and suggest contacting a human."
    )


def make_oss_call(
    model_name: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 512,
) -> str:
    """
    Low-level call to the GPT-OSS chat endpoint.
    """
    payload = {
        "model": "gpt-oss:20b",
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": False,
    }

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_oss_model(
    model_name: str,
    tenant: TenantConfig,
    session: SessionState,
    user_text: str,
) -> str:
    """
    High-level model call used by the bot.
    Builds proper system prompt + context and returns a clean answer.
    """

    system_message = {"role": "system", "content": build_system_prompt(tenant)}
    user_message = {"role": "user", "content": user_text}

    # You can extend this to include more history:
    history = session.context.get("history", [])
    messages = [system_message] + history + [user_message]

    # Make the call
    result = make_oss_call(model_name, messages)

    # Update session history (only last N messages to control context size)
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": result})
    session.context["history"] = history[-10:]  # keep last 10 turns

    # Enforce reply length
    if len(result) > tenant.max_reply_length:
        result = result[: tenant.max_reply_length - 3] + "..."

    return result
