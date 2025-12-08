import unittest

from bot.config import InMemoryConfigStore, TenantConfig
from bot.core import handle_message
from bot.state import InMemoryStateStore
from bot.knowledge import get_studio_info


def make_config_store():
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


class ConversationCompletionTests(unittest.TestCase):
    def setUp(self):
        self.config_store = make_config_store()
        self.tenant_id = "store-1"

    def _run_conversation(self, user_id: str, messages):
        state_store = InMemoryStateStore()
        replies = []
        for text in messages:
            reply = handle_message(
                tenant_id=self.tenant_id,
                user_id=user_id,
                text=text,
                message_id=f"msg-{user_id}",
                state_store=state_store,
                config_store=self.config_store,
            )
            replies.append(reply)

        session = state_store.get_session(self.tenant_id, user_id)
        return replies, session

    def test_multiple_paths_end_cleanly(self):
        scenarios = [
            [
                "Oi, quero saber dos serviços",  # list services
                "horário de sábado",  # hours
                "obrigada",  # closing
            ],
            [
                "onde fica o estúdio?",  # address
                "quero marcar",  # booking start
                "Brow Lamination Simples",  # service
                "12/06",  # date
                "14:00",  # time
                "João",  # name
                "21988887777",  # phone
            ],
            [
                "qual serviço você recomenda?",  # advice
                "quero algo natural",  # follow-up remains general
                "tchau",  # closing
            ],
        ]

        for idx, messages in enumerate(scenarios):
            user_id = f"user-{idx}"
            replies, session = self._run_conversation(user_id, messages)

            self.assertGreaterEqual(len(replies), len(messages))
            self.assertEqual(session.context.get("history_len"), len(messages))
            self.assertTrue(
                session.context.get("closed") or not session.context.get("booking"),
                "Session should be closed or booking cleared",
            )


if __name__ == "__main__":
    unittest.main()
