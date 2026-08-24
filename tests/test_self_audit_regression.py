from pathlib import Path

from humanizer_os.analyzer import Analyzer

ROOT = Path(__file__).resolve().parents[1]


def test_public_product_copy_has_no_warning_level_findings() -> None:
    analyzer = Analyzer()
    sources = [
        ROOT / "README.md",
        ROOT / "SKILL.md",
        ROOT / "docs" / "BRAND.md",
    ]

    for source in sources:
        report = analyzer.audit(
            source.read_text(encoding="utf-8"),
            locale="en",
            genre="docs",
            source=str(source.relative_to(ROOT)),
            min_confidence="low",
        )
        warnings = [
            finding
            for finding in report.findings
            if finding.severity in {"warning", "error"}
        ]
        assert not warnings, (
            source,
            [(item.rule_id, item.line, item.excerpt) for item in warnings],
        )
