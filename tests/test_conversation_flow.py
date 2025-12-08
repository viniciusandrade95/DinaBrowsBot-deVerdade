import unittest

from bot.config import InMemoryConfigStore, TenantConfig
from bot.core import handle_message
from bot.state import InMemoryStateStore


def make_config_store():
    demo_tenant = TenantConfig(
        tenant_id="store-1",
        name="Sneaker Planet",
        tone="friendly",
        language="en",
        currency="EUR",
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


class ConversationFlowTests(unittest.TestCase):
    def setUp(self):
        self.config_store = make_config_store()
        self.state_store = InMemoryStateStore()
        self.tenant_id = "store-1"
        self.user_id = "test-user"

    def test_conversation_progresses_and_updates_history(self):
        messages = [
            "Hi there",
            "What time do you close today?",
            "Do you have running shoes in size 42?",
            "Thanks, bye",
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

        # Conversation metadata should capture the number of turns
        session = self.state_store.get_session(self.tenant_id, self.user_id)
        self.assertEqual(session.context.get("history_len"), len(messages))

        # Replies should not get stuck repeating the same message across turns
        self.assertGreaterEqual(len(set(replies)), 2)

    def test_repeated_noise_does_not_spin_forever(self):
        """Very short inputs are treated as noise but still return quickly."""

        for _ in range(10):
            reply = handle_message(
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                text="?",
                message_id="noise",
                state_store=self.state_store,
                config_store=self.config_store,
            )
            self.assertIn("rephrase", reply.lower())

        session = self.state_store.get_session(self.tenant_id, self.user_id)
        self.assertEqual(session.context.get("history_len"), 10)

    def test_air_zoom_stock_conversation_over_multiple_turns(self):
        """Simulate a 5-turn stock inquiry to ensure responses stay on track."""

        messages = [
            "Do you have Air Zoom in size 42?",
            "It's the Nike Air Zoom Pegasus",
            "Size 42 EU",
            "Do you deliver to Porto?",
            "Thanks!",
        ]

        expected_fragments = [
            "checking availability",  # initial stock prompt
            "help with sneakers",  # generic guidance with suggestions
            "checking availability",  # size mention loops back to stock prompt
            "courier delivery",  # shipping branch
            "thanks for chatting",  # closing branch
        ]

        replies = []

        for text, fragment in zip(messages, expected_fragments):
            reply = handle_message(
                tenant_id=self.tenant_id,
                user_id=self.user_id,
                text=text,
                message_id="air-zoom-seq",
                state_store=self.state_store,
                config_store=self.config_store,
            )
            replies.append(reply)
            self.assertIn(fragment, reply.lower())

        session = self.state_store.get_session(self.tenant_id, self.user_id)
        self.assertEqual(session.context.get("history_len"), len(messages))
        self.assertGreaterEqual(len(set(replies)), 3)

    def test_two_turn_stock_acknowledgement(self):
        greeting = handle_message(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            text="hello",
            message_id="stock-hello",
            state_store=self.state_store,
            config_store=self.config_store,
        )
        self.assertIn("hi", greeting.lower())

        stock_reply = handle_message(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            text="do you have air zoom size 43",
            message_id="stock-check",
            state_store=self.state_store,
            config_store=self.config_store,
        )

        lower_reply = stock_reply.lower()
        self.assertIn("air zoom", lower_reply)
        self.assertIn("size 43", lower_reply)
        self.assertIn("color", lower_reply)
        self.assertTrue("pickup" in lower_reply or "delivery" in lower_reply)

        session = self.state_store.get_session(self.tenant_id, self.user_id)
        self.assertEqual(session.context.get("requested_product"), "air zoom")
        self.assertEqual(session.context.get("requested_size"), "43")


if __name__ == "__main__":
    unittest.main()
