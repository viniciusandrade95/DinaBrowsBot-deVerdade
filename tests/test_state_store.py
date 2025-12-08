import json
import tempfile
from pathlib import Path
import unittest

from bot.state import FileStateStore, InMemoryStateStore, SessionState


class InMemoryStateStoreTests(unittest.TestCase):
    def test_get_and_save_session(self):
        store = InMemoryStateStore()
        session = store.get_session("t1", "u1")
        session.context["foo"] = "bar"
        store.save_session(session)

        reloaded = store.get_session("t1", "u1")
        self.assertEqual(reloaded.context["foo"], "bar")

    def test_append_event(self):
        store = InMemoryStateStore()
        store.append_event("t1", "u1", {"type": "message"})

        session = store.get_session("t1", "u1")
        self.assertEqual(session.context["events"], [{"type": "message"}])

    def test_delete_session(self):
        store = InMemoryStateStore()
        store.get_session("t1", "u1")
        store.delete_session("t1", "u1")
        self.assertNotIn("t1:u1", store._store)


class FileStateStoreTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileStateStore(base_path=tmp)
            session = SessionState(tenant_id="t1", user_id="u1")
            session.context["cart"] = {"items": 2}
            store.save_session(session)

            reloaded = store.get_session("t1", "u1")
            self.assertEqual(reloaded.context["cart"], {"items": 2})

            # Inspect raw file for correctness
            raw = json.loads(Path(tmp).joinpath("t1__u1.json").read_text())
            self.assertEqual(raw["tenant_id"], "t1")
            self.assertEqual(raw["user_id"], "u1")

    def test_delete_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileStateStore(base_path=tmp)
            store.save_session(SessionState(tenant_id="t1", user_id="u1"))
            store.delete_session("t1", "u1")

            self.assertFalse(Path(tmp).joinpath("t1__u1.json").exists())

    def test_append_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileStateStore(base_path=tmp)
            store.append_event("t1", "u1", {"type": "ping"})
            session = store.get_session("t1", "u1")

            self.assertEqual(session.context.get("events"), [{"type": "ping"}])


if __name__ == "__main__":
    unittest.main()
