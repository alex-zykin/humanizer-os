from pathlib import Path

from humanizer_os import Analyzer, verify_texts

ROOT = Path(__file__).resolve().parents[1]
BEFORE = ROOT / "examples" / "real-world-ai-before.md"
AFTER = ROOT / "examples" / "real-world-ai-after.md"


def test_real_world_ai_demo_is_reproducible() -> None:
    before_text = BEFORE.read_text(encoding="utf-8")
    after_text = AFTER.read_text(encoding="utf-8")
    analyzer = Analyzer()

    before = analyzer.audit(before_text, locale="en", genre="article")
    after = analyzer.audit(after_text, locale="en", genre="article")

    assert len(before.findings) == 5
    assert {item.rule_id for item in before.findings} == {"EN-LANG-001", "EN-RHET-003"}
    assert not after.findings
    assert before.metrics["words"] == 348
    assert after.metrics["words"] < before.metrics["words"]

    verification = verify_texts(before_text, after_text)
    assert verification.ok
    assert verification.original_count == 8
    assert verification.revised_count == 8
