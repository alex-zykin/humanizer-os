from humanizer_os.analyzer import Analyzer


def ids(text: str, **kwargs: object) -> set[str]:
    return {item.rule_id for item in Analyzer().audit(text, **kwargs).findings}


def test_english_surface_rules() -> None:
    text = (
        "In today's fast-paced world, this is not just a tool, but a pivotal game-changer. "
        "In conclusion, the possibilities are endless."
    )
    found = ids(text, locale="en", genre="landing")
    assert {"EN-OPEN-001", "EN-RHET-001", "EN-LANG-001", "EN-RHET-003", "EN-CONTENT-001"} <= found


def test_russian_surface_rules() -> None:
    text = (
        "В современном мире это не просто инструмент, а революционное решение. "
        "Таким образом, возможности безграничны."
    )
    found = ids(text, locale="ru", genre="landing")
    assert {"RU-OPEN-001", "RU-RHET-001", "RU-LANG-006", "RU-RHET-004", "RU-CONTENT-001"} <= found


def test_code_and_quotes_are_ignored() -> None:
    text = 'Use `in order to` in the exact parser test. The customer said “In conclusion”.'
    found = ids(text, locale="en")
    assert "EN-LANG-004" not in found
    assert "EN-RHET-003" not in found


def test_internal_artifacts_are_not_ignored_in_quotes() -> None:
    found = ids('The output contains "turn7search3".', locale="en")
    assert "EN-ART-003" in found


def test_confidence_filter() -> None:
    text = "This — sentence — has — many — interruptions — for its length."
    all_ids = ids(text * 10, locale="en", min_confidence="low")
    high_ids = ids(text * 10, locale="en", min_confidence="high")
    assert "EN-STYLE-002" in all_ids
    assert "EN-STYLE-002" not in high_ids


def test_short_sentence_stack() -> None:
    text = "The build failed. No logs. No trace. No clue. We rolled it back and opened an incident."
    assert "EN-STYLE-003" in ids(text, locale="en", genre="article")


def test_repeated_starts() -> None:
    text = (
        "We shipped the parser. We shipped the CLI. We shipped the tests. "
        "The team reviewed the release. The package is ready."
    )
    assert "EN-STRUCT-003" in ids(text * 2, locale="en", genre="article")


def test_report_contains_line_and_column() -> None:
    report = Analyzer().audit("First line.\nIn order to ship, test.", locale="en")
    finding = next(item for item in report.findings if item.rule_id == "EN-LANG-004")
    assert finding.line == 2
    assert finding.column == 1


def test_unknown_rule_filter_is_an_error() -> None:
    import pytest

    with pytest.raises(ValueError, match="Unknown rule"):
        Analyzer().audit("Plain text.", locale="en", only_rules=["EN-NOPE-999"])


def test_only_rule_must_match_resolved_locale() -> None:
    import pytest

    with pytest.raises(ValueError, match="belongs to ru"):
        Analyzer().audit("Plain English text.", locale="en", only_rules=["RU-LANG-007"])


def test_chatgpt_utm_marker_is_visible_inside_url() -> None:
    report = Analyzer().audit(
        "See https://example.com/page?utm_source=chatgpt.com for the draft.",
        locale="en",
    )
    assert "EN-ART-003" in {item.rule_id for item in report.findings}


def test_placeholder_rule_ignores_markdown_links() -> None:
    en = Analyzer().audit("Read [source](https://example.com).", locale="en")
    ru = Analyzer().audit("Смотрите [источники](https://example.com).", locale="ru")
    assert "EN-ART-004" not in {item.rule_id for item in en.findings}
    assert "RU-ART-004" not in {item.rule_id for item in ru.findings}


def test_placeholder_rule_still_finds_unresolved_fields() -> None:
    en = Analyzer().audit("Published on [date: add before launch].", locale="en")
    ru = Analyzer().audit("Опубликовать [дата: добавить перед запуском].", locale="ru")
    assert "EN-ART-004" in {item.rule_id for item in en.findings}
    assert "RU-ART-004" in {item.rule_id for item in ru.findings}
