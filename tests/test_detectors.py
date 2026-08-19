from humanizer_os.analyzer import Analyzer


def finding_ids(text: str, locale: str = "en", genre: str = "article") -> set[str]:
    return {item.rule_id for item in Analyzer().audit(text, locale=locale, genre=genre).findings}


def test_uniform_paragraph_detector() -> None:
    paragraph = " ".join(["The release candidate passed the parser test and the team recorded every result carefully."] * 3)
    text = "\n\n".join([paragraph] * 4)
    assert "EN-STRUCT-001" in finding_ids(text)


def test_uniform_sentence_detector() -> None:
    sentence = "The team checked every parser result before approving the release today."
    text = " ".join([sentence] * 14)
    assert "EN-STRUCT-002" in finding_ids(text)


def test_transition_density_detector() -> None:
    body = "The team checked the complete result set and recorded the decision with enough detail for review."
    text = "\n\n".join(
        [
            f"Additionally, {body}",
            f"Furthermore, {body}",
            f"Moreover, {body}",
            f"The final section records the remaining risk. {body}",
        ]
    )
    assert "EN-STRUCT-004" in finding_ids(text)


def test_dash_density_detector() -> None:
    text = ("This clause — interrupts the point — and the next clause — interrupts it again — " * 7).strip()
    assert "EN-STYLE-002" in finding_ids(text)


def test_list_density_detector() -> None:
    text = "\n".join(
        [
            "- First independent item",
            "- Second independent item",
            "- Third independent item",
            "- Fourth independent item",
            "- Fifth independent item",
            "- Sixth independent item",
            "A short note",
            "Another short note",
        ]
    )
    assert "EN-FMT-004" in finding_ids(text * 2)


def test_russian_transition_density() -> None:
    body = "Команда проверила результаты и записала решение достаточно подробно для повторной проверки всей командой."
    text = "\n\n".join(
        [
            f"Кроме того, {body}",
            f"Более того, {body}",
            f"При этом {body}",
            f"Последний абзац описывает риск. {body}",
        ]
    )
    assert "RU-STRUCT-004" in finding_ids(text, locale="ru")


def test_repeated_starts_ignore_markdown_list_items() -> None:
    text = "\n".join(
        [
            "- The engine preserves facts.",
            "- The engine preserves links.",
            "- The engine preserves code.",
            "- The engine preserves line endings.",
            "- The engine preserves file modes.",
        ]
    )
    report = Analyzer().audit(text, locale="en", genre="docs")
    assert "EN-STRUCT-003" not in {item.rule_id for item in report.findings}


def test_short_sentence_stack_ignores_markdown_list_items() -> None:
    text = "\n".join(["- Fast.", "- Local.", "- Explainable.", "- Tested."])
    report = Analyzer().audit(text, locale="en", genre="docs")
    assert "EN-STRUCT-001" not in {item.rule_id for item in report.findings}


def test_structural_detectors_ignore_markdown_table_rows() -> None:
    text = "\n".join(
        [
            "| Rule | Meaning |",
            "|---|---|",
            "| EN-ONE | Fast. |",
            "| EN-TWO | Local. |",
            "| EN-THREE | Tested. |",
            "| EN-FOUR | Typed. |",
            "| EN-FIVE | Documented. |",
        ]
    )
    ids = finding_ids(text * 3, genre="docs")
    assert "EN-STRUCT-003" not in ids
    assert "EN-STRUCT-005" not in ids


def test_repeated_starts_ignore_markdown_field_labels() -> None:
    text = " ".join(
        [
            "A rule entry follows.",
            "**Finding:** Review the wrapper.",
            "**Finding:** Review the source.",
            "**Finding:** Review the ending.",
            "The catalog keeps these labels intentionally.",
        ]
    )
    assert "EN-STRUCT-003" not in finding_ids(text, genre="docs")
