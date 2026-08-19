from humanizer_os.rewriter import Rewriter


def test_applies_safe_english_fixes_and_preserves_case() -> None:
    report = Rewriter().fix("In order to ship, test now. We work in order to learn.", locale="en")
    assert report.revised == "To ship, test now. We work to learn."
    assert report.verification.ok
    assert [item.rule_id for item in report.changes] == ["EN-LANG-004", "EN-LANG-004"]


def test_applies_safe_russian_fixes_and_preserves_case() -> None:
    report = Rewriter().fix("На сегодняшний день мы работаем для того чтобы запустить тест.", locale="ru")
    assert report.revised == "Сейчас мы работаем чтобы запустить тест."
    assert report.verification.ok


def test_does_not_modify_code_or_urls() -> None:
    text = "Run `in order to` exactly. Read https://example.com/in-order-to."
    report = Rewriter().fix(text, locale="en")
    assert report.revised == text


def test_fix_is_idempotent() -> None:
    first = Rewriter().fix("At this point in time we build in order to ship.", locale="en")
    second = Rewriter().fix(first.revised, locale="en")
    assert first.revised == "Now we build to ship."
    assert not second.changed


def test_only_safe_rules_are_rewritten() -> None:
    text = "In today's fast-paced world, this is not just a tool, but a game-changer."
    report = Rewriter().fix(text, locale="en")
    assert report.revised == text
    assert not report.changes


def test_fix_does_not_modify_straight_quoted_text() -> None:
    original = 'The phrase "in order to" appears in the style guide.'
    report = Rewriter().fix(original, locale="en")
    assert report.revised == original
    assert not report.changed


def test_fix_does_not_modify_markdown_blockquote() -> None:
    original = "> In order to ship, run the checks.\n\nThe note stays outside."
    report = Rewriter().fix(original, locale="en")
    assert report.revised == original


def test_non_universal_phrase_is_reported_but_not_fixed() -> None:
    original = "For the purpose of testing, keep this construction."
    report = Rewriter().fix(original, locale="en")
    finding = next(item for item in report.before_audit.findings if item.rule_id == "EN-LANG-004")
    assert not finding.fixable
    assert report.revised == original
