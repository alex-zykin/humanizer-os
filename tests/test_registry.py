import pytest

from humanizer_os.registry import RuleRegistry


def test_builtin_catalog_is_substantial() -> None:
    registry = RuleRegistry()
    assert len(registry.list("en")) >= 30
    assert len(registry.list("ru")) >= 30


def test_rule_ids_are_unique() -> None:
    registry = RuleRegistry()
    ids = [rule.id for rule in registry.list()]
    assert len(ids) == len(set(ids))


def test_genre_exclusions_are_applied() -> None:
    registry = RuleRegistry()
    legal_ids = {rule.id for rule in registry.active("en", "legal", 10_000)}
    assert "EN-LANG-004" not in legal_ids
    assert "EN-ART-003" in legal_ids


def test_unknown_rule_has_clear_error() -> None:
    with pytest.raises(KeyError, match="Unknown rule"):
        RuleRegistry().get("EN-NOT-REAL")


def test_unknown_genre_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported genre"):
        RuleRegistry().list("en", "unknown")


def test_unknown_locale_is_rejected_when_listing_rules() -> None:
    with pytest.raises(ValueError, match="Unsupported locale"):
        RuleRegistry().list("de")
