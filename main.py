# main.py
from bot.state import InMemoryStateStore
from bot.core import handle_message
from app import build_demo_config_store


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
