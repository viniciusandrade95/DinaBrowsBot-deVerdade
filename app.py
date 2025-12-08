"""FastAPI server exposing the chat bot for deployment platforms like Railway."""

import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

from bot.core import handle_message
from bot.settings import build_state_store
from bot.config import InMemoryConfigStore, TenantConfig
from bot.whatsapp import send_text_message
from bot.contact_log import log_contact_number
from bot.knowledge import get_studio_info


def build_demo_config_store() -> InMemoryConfigStore:
    info = get_studio_info()
    demo_tenant = TenantConfig(
        tenant_id="store-1",
        name=info["name"],
        tone="friendly",
        language="pt",
        currency="BRL",
        default_model="20b",
        allow_chitchat=False,
        max_reply_length=600,
        store_info=info,
    )
    return InMemoryConfigStore({"store-1": demo_tenant})


app = FastAPI(title="DinaBrowsBot API")
config_store = build_demo_config_store()
state_store = build_state_store()
logger = logging.getLogger(__name__)


def normalize_brazilian_number(number: str) -> str:
    """Normalize Brazilian WhatsApp numbers to include exactly one '9' after the DDD."""

    if not number:
        return number

    stripped = number.strip()
    digits_only = "".join(ch for ch in stripped if ch.isdigit())
    has_plus = stripped.startswith("+")

    if digits_only.startswith("55") and len(digits_only) >= 4:
        # 55 + area (2) + subscriber. Ensure a single leading '9' after DDD.
        prefix = digits_only[:4]
        subscriber = digits_only[4:]

        if subscriber.startswith("99"):
            subscriber = f"9{subscriber[2:]}"
        elif not subscriber.startswith("9"):
            subscriber = f"9{subscriber}"

        digits_only = f"{prefix}{subscriber}"
        return f"+{digits_only}" if has_plus or stripped.startswith("+55") else digits_only

    return stripped


class ChatRequest(BaseModel):
    text: str
    tenant_id: str = "store-1"
    user_id: str
    message_id: Optional[str] = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat")
def chat_endpoint(payload: ChatRequest):
    try:
        reply = handle_message(
            tenant_id=payload.tenant_id,
            user_id=payload.user_id,
            text=payload.text,
            message_id=payload.message_id or "http",
            state_store=state_store,
            config_store=config_store,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"reply": reply}


@app.get("/webhook", response_class=PlainTextResponse)
def whatsapp_verify(mode: str, challenge: str, token: str):
    """Verification endpoint for the WhatsApp webhook setup."""

    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    if verify_token and mode == "subscribe" and token == verify_token:
        return challenge
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages and reply using the bot logic."""

    data = await request.json()
    try:
        change = data["entry"][0]["changes"][0]["value"]
        messages = change.get("messages", [])
        if not messages:
            return {"status": "ignored"}

        message = messages[0]
        from_number = message.get("from")
        if not from_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing sender number",
            )
        text_body = message.get("text", {}).get("body", "")
        message_id = message.get("id", "whatsapp")
    except (KeyError, IndexError) as exc:
        logger.exception("Malformed webhook payload: %s", data)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload") from exc

    try:
        sanitized_number = from_number
        #sanitized_number = normalize_brazilian_number(from_number)
    except Exception as exc:
        logger.exception("Failed to normalize number %s: %s", from_number, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sender number"
        ) from exc

    try:  # Notify internal number about the new contact; failures shouldn't block processing
        send_text_message(
            to="+5521996973295",
            body=f"Novo contato via WhatsApp: {sanitized_number}",
        )
    except Exception as exc:  # pragma: no cover - network call
        logger.warning("Failed to forward contact %s: %s", sanitized_number, exc)

    reply = handle_message(
        tenant_id="store-1",
        user_id=sanitized_number,
        text=text_body,
        message_id=message_id,
        state_store=state_store,
        config_store=config_store,
    )

    log_contact_number(sanitized_number)

    try:
        send_text_message(to=sanitized_number, body=reply)
    except Exception as exc:  # pragma: no cover - network call
        logger.exception("Failed to send WhatsApp message: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to send reply") from exc

    return {"status": "sent", "reply": reply}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,
    )
