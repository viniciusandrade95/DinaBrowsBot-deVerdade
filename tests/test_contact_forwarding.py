"""Ensure inbound WhatsApp contacts are forwarded to the audit number."""

import asyncio
import json

from fastapi import Request

import app as app_module


def build_payload(from_number: str, text: str = "oi") -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": from_number,
                                    "id": "wamid.test",
                                    "text": {"body": text},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def test_forward_contact_number(monkeypatch):
    calls = []

    def fake_send_text_message(**kwargs):
        calls.append(kwargs)
        return {"status": "ok"}

    monkeypatch.setattr(app_module, "send_text_message", fake_send_text_message)
    monkeypatch.setattr(app_module, "handle_message", lambda **_: "resposta")

    payload = build_payload("+552187654321")
    body = json.dumps(payload).encode()

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/webhook",
        "headers": [(b"content-type", b"application/json")],
    }
    request = Request(scope, receive)

    response = asyncio.get_event_loop().run_until_complete(
        app_module.whatsapp_webhook(request)
    )

    assert response["status"] == "sent"
    assert any(call.get("to") == "353830867975" for call in calls)
    assert any(
        call.get("to") == "+5521987654321" and call.get("body") == "resposta"
        for call in calls
    )
