"""FastAPI server exposing the chat bot for deployment platforms like Railway."""

import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

from bot.core import handle_message
from bot.state import InMemoryStateStore
from bot.config import InMemoryConfigStore, TenantConfig
from bot.whatsapp import send_text_message


def build_demo_config_store() -> InMemoryConfigStore:
    demo_tenant = TenantConfig(
        tenant_id="store-1",
        name="Sneaker Planet",
        tone="friendly",
        language="en",
        currency="€",
        default_model="20b",
        allow_chitchat=True,
        max_reply_length=600,
        store_info={
            "openingHours": "Mon–Sat 10:00–20:00",
            "address": "123 Sneaker Street",
            "phone": "+49 123 456 789",
        },
    )
    return InMemoryConfigStore({"store-1": demo_tenant})


app = FastAPI(title="DinaBrowsBot API")
config_store = build_demo_config_store()
state_store = InMemoryStateStore()
logger = logging.getLogger(__name__)


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
        text_body = message.get("text", {}).get("body", "")
        message_id = message.get("id", "whatsapp")
    except (KeyError, IndexError) as exc:
        logger.exception("Malformed webhook payload: %s", data)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload") from exc

    reply = handle_message(
        tenant_id="store-1",
        user_id=from_number,
        text=text_body,
        message_id=message_id,
        state_store=state_store,
        config_store=config_store,
    )

    try:
        send_text_message(to=from_number, body=reply)
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
