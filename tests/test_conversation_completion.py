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
                "Hi, I'm interested in running shoes",
                "What time do you open tomorrow?",
                "Thanks for your help",
            ],
            [
                "Where are you located?",
                "I'd like to visit today",
                "bye",
            ],
            [
                "Can you ship to Berlin?",
                "I want the Nike Air Zoom Pegasus",
                "Thanks!",
            ],
            [
                "I need to return a pair of shoes",
                "They're unused and boxed",
                "thank you",
            ],
            [
                "What's the price range for Air Zoom?",
                "How do I place an order?",
                "I appreciate it",
            ],
        ]

        for idx, messages in enumerate(scenarios):
            user_id = f"user-{idx}"
            replies, session = self._run_conversation(user_id, messages)

            self.assertIn("thanks for chatting", replies[-1].lower())
            self.assertEqual(session.context.get("history_len"), len(messages))
            self.assertTrue(session.context.get("closed"))
            self.assertEqual(session.flow, "CLOSED")


if __name__ == "__main__":
    unittest.main()
