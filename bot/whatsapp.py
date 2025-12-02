"""Utility functions to send outbound WhatsApp messages via Meta's Graph API."""
import os
from typing import Any, Dict, List, Optional

import requests


class WhatsAppConfigError(RuntimeError):
    """Raised when required WhatsApp configuration is missing."""


DEFAULT_API_VERSION = "v22.0"


def _get_env(var_name: str, override: Optional[str]) -> str:
    value = override if override is not None else os.getenv(var_name)
    if not value:
        raise WhatsAppConfigError(f"Missing required setting: {var_name}")
    return value


def _build_url(phone_number_id: str, api_version: str) -> str:
    return f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"


def send_template_message(
    *,
    to: str,
    template_name: str,
    language_code: str = "en_US",
    components: Optional[List[Dict[str, Any]]] = None,
    access_token: Optional[str] = None,
    phone_number_id: Optional[str] = None,
    api_version: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Send a WhatsApp template message through the Graph API.

    Environment fallbacks:
    - ``WHATSAPP_ACCESS_TOKEN``
    - ``WHATSAPP_PHONE_NUMBER_ID``
    - ``WHATSAPP_API_VERSION`` (defaults to ``v22.0``)
    """

    token = _get_env("WHATSAPP_ACCESS_TOKEN", access_token)
    phone_id = _get_env("WHATSAPP_PHONE_NUMBER_ID", phone_number_id)
    version = api_version or os.getenv("WHATSAPP_API_VERSION", DEFAULT_API_VERSION)

    url = _build_url(phone_id, version)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }
    if components:
        payload["template"]["components"] = components

    response = requests.post(url, headers=headers, json=payload, timeout=timeout)

    if response.status_code >= 400:
        raise RuntimeError(
            f"WhatsApp API error {response.status_code}: {response.text}"
        )

    return response.json()


def send_text_message(
    *,
    to: str,
    body: str,
    access_token: Optional[str] = None,
    phone_number_id: Optional[str] = None,
    api_version: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """Send a plain text WhatsApp message using the Graph API."""

    token = _get_env("WHATSAPP_ACCESS_TOKEN", access_token)
    phone_id = _get_env("WHATSAPP_PHONE_NUMBER_ID", phone_number_id)
    version = api_version or os.getenv("WHATSAPP_API_VERSION", DEFAULT_API_VERSION)

    url = _build_url(phone_id, version)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=timeout)

    if response.status_code >= 400:
        raise RuntimeError(
            f"WhatsApp API error {response.status_code}: {response.text}"
        )

    return response.json()
