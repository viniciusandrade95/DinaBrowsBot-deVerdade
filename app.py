"""FastAPI server exposing the chat bot for deployment platforms like Railway."""
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from bot.core import handle_message
from bot.state import InMemoryStateStore
from bot.config import InMemoryConfigStore, TenantConfig


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,
    )
