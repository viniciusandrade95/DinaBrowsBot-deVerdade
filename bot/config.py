# bot/config.py
from dataclasses import dataclass
from typing import Literal, Dict

from .knowledge import get_studio_info

Tone = Literal["friendly", "professional", "playful"]


@dataclass
class TenantConfig:
    tenant_id: str
    name: str
    tone: Tone
    language: str
    currency: str
    default_model: str  # "20b" or "120b"
    allow_chitchat: bool
    max_reply_length: int
    store_info: Dict[str, str]


class ConfigStore:
    """Abstract config store."""

    def load_tenant_config(self, tenant_id: str) -> TenantConfig:
        raise NotImplementedError


class InMemoryConfigStore(ConfigStore):
    """Simple per-tenant config."""

    def __init__(self, configs: Dict[str, TenantConfig]):
        self._configs = configs

    def load_tenant_config(self, tenant_id: str) -> TenantConfig:
        if tenant_id not in self._configs:
            info = get_studio_info()
            return TenantConfig(
                tenant_id=tenant_id,
                name=info["name"],
                tone="friendly",
                language="pt",
                currency="BRL",
                default_model="20b",
                allow_chitchat=False,
                max_reply_length=800,
                store_info=info,
            )
        return self._configs[tenant_id]
