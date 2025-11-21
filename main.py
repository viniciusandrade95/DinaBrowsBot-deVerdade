# main.py
from bot.config import TenantConfig, InMemoryConfigStore
from bot.state import InMemoryStateStore
from bot.core import handle_message


def build_demo_config_store():
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


if __name__ == "__main__":
    config_store = build_demo_config_store()
    state_store = InMemoryStateStore()

    tenant_id = "store-1"
    user_id = "user-abc"

    while True:
        user_text = input("User: ")
        if user_text.lower() in {"quit", "exit"}:
            break

        reply = handle_message(
            tenant_id=tenant_id,
            user_id=user_id,
            text=user_text,
            message_id="dummy",
            state_store=state_store,
            config_store=config_store,
        )
        print("Bot :", reply)
