import json
from datetime import datetime, timezone

from bot.contact_log import load_contact_log, log_contact_number


def test_creates_new_contact_entry(tmp_path):
    log_path = tmp_path / "contacts.json"
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    log_contact_number("+5521987654321", log_path=log_path, now=now)

    data = json.loads(log_path.read_text())
    assert data == [
        {
            "number": "+5521987654321",
            "first_seen": now.isoformat(),
            "last_seen": now.isoformat(),
            "count": 1,
        }
    ]


def test_updates_existing_contact(tmp_path):
    log_path = tmp_path / "contacts.json"
    first = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    second = datetime(2024, 1, 2, 8, 30, 0, tzinfo=timezone.utc)

    log_contact_number("+5521987654321", log_path=log_path, now=first)
    log_contact_number("+5521987654321", log_path=log_path, now=second)

    data = load_contact_log(log_path)
    assert data[0]["first_seen"] == first.isoformat()
    assert data[0]["last_seen"] == second.isoformat()
    assert data[0]["count"] == 2


def test_logs_multiple_numbers(tmp_path):
    log_path = tmp_path / "contacts.json"
    log_contact_number("+5521987654321", log_path=log_path)
    log_contact_number("+14155552671", log_path=log_path)

    numbers = {entry["number"] for entry in load_contact_log(log_path)}
    assert numbers == {"+5521987654321", "+14155552671"}
