"""Tests for Brazilian phone normalization used in the webhook."""

from app import normalize_brazilian_number


def test_inserts_missing_nine_for_brazil_number():
    assert normalize_brazilian_number("+552187654321") == "+5521987654321"


def test_keeps_valid_brazil_number_intact():
    assert normalize_brazilian_number("5521987654321") == "5521987654321"


def test_non_brazil_numbers_are_untouched():
    assert normalize_brazilian_number("+14155552671") == "+14155552671"
