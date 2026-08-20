from pathlib import Path

from humanizer_os import Analyzer, verify_texts

ROOT = Path(__file__).resolve().parents[1]
BEFORE = ROOT / "examples" / "product-launch-before.md"
AFTER = ROOT / "examples" / "product-launch-after.md"


def test_product_launch_demo_is_reproducible() -> None:
    analyzer = Analyzer()
    before_text = BEFORE.read_text(encoding="utf-8")
    after_text = AFTER.read_text(encoding="utf-8")

    before_report = analyzer.audit(before_text, locale="en", genre="landing")
    after_report = analyzer.audit(after_text, locale="en", genre="landing")

    expected_rule_ids = {
        "EN-OPEN-001",
        "EN-RHET-001",
        "EN-LANG-001",
        "EN-LANG-005",
        "EN-LANG-006",
        "EN-LANG-002",
        "EN-RHET-003",
        "EN-CONTENT-001",
    }

    assert len(before_report.findings) == 10
    assert {finding.rule_id for finding in before_report.findings} == expected_rule_ids
    assert not after_report.findings

    verification = verify_texts(before_text, after_text)
    assert verification.ok
    assert verification.original_count == 6
    assert verification.revised_count == 6
