# bot/config.py
from dataclasses import dataclass
from typing import Literal, Dict


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
    """Simple per-tenant config, replace with DB later."""

    def __init__(self, configs: Dict[str, TenantConfig]):
        self._configs = configs

    def load_tenant_config(self, tenant_id: str) -> TenantConfig:
        if tenant_id not in self._configs:
            # default config if not found
            return TenantConfig(
                tenant_id=tenant_id,
                name=f"Store {tenant_id}",
                tone="friendly",
                language="en",
                currency="USD",
                default_model="20b",
                allow_chitchat=True,
                max_reply_length=800,
                store_info={
                    "openingHours": "Mon–Fri 09:00–18:00",
                    "address": "Main street 123",
                    "phone": "+00 000 000 000",
                },
            )
        return self._configs[tenant_id]
