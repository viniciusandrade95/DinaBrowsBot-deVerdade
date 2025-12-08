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


class ConversationFlowTests(unittest.TestCase):
    def setUp(self):
        self.config_store = make_config_store()
        self.state_store = InMemoryStateStore()
        self.tenant_id = "store-1"
        self.user_id = "test-user"

    def test_basic_info_flow(self):
        messages = [
            "Oi",  # greeting
            "qual é o endereço?",  # location
            "qual horário funciona?",  # hours
            "obrigado",  # closing
        ]
        replies = []

        for text in messages:
            reply = handle_message(
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                text=text,
                message_id="unit-test",
                state_store=self.state_store,
                config_store=self.config_store,
            )
            replies.append(reply)
            self.assertTrue(reply.strip(), "Bot returned an empty reply")

        session = self.state_store.get_session(self.tenant_id, self.user_id)
        self.assertEqual(session.context.get("history_len"), len(messages))
        self.assertTrue(any("DinaBrows" in r for r in replies))
        self.assertTrue(session.context.get("closed"))

    def test_booking_flow(self):
        steps = [
            "quero agendar",  # start
            "brow lamination completa",  # service
            "10/06",  # date
            "15:00",  # time
            "Ana",  # name
            "+55 21 99999-0000",  # phone
        ]

        last_reply = ""
        for text in steps:
            last_reply = handle_message(
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                text=text,
                message_id="booking",
                state_store=self.state_store,
                config_store=self.config_store,
            )

        self.assertIn("Agendamento registrado", last_reply)
        session = self.state_store.get_session(self.tenant_id, self.user_id)
        self.assertNotIn("booking", session.context)

    def test_service_details_and_advice(self):
        detail_reply = handle_message(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            text="me fala sobre design de sobrancelhas",
            message_id="detail",
            state_store=self.state_store,
            config_store=self.config_store,
        )
        self.assertIn("Design de Sobrancelhas", detail_reply)

        advice_reply = handle_message(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            text="nao sei qual serviço escolher",
            message_id="advice",
            state_store=self.state_store,
            config_store=self.config_store,
        )
        self.assertIn("natural", advice_reply.lower())


if __name__ == "__main__":
    unittest.main()
