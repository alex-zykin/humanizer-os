from __future__ import annotations

import json
from dataclasses import replace

from humanizer_os.analyzer import Analyzer
from humanizer_os.models import AuditReport, LanguageGuess, VerificationReport
from humanizer_os.output import (
    render_audit_text,
    render_rewrite_text,
    render_rules_text,
    reports_sarif,
    verification_json,
)
from humanizer_os.registry import RuleRegistry
from humanizer_os.rewriter import Rewriter


def test_render_clean_audit() -> None:
    report = Analyzer().audit("The launch starts Monday.", locale="en", source="<text>")
    text = render_audit_text(report)
    assert "OK" in text


def test_render_rewrite_states() -> None:
    unchanged = Rewriter().fix("The launch starts Monday.", locale="en")
    assert "No safe deterministic fixes" in render_rewrite_text(unchanged)

    changed = Rewriter().fix("In order to ship, test.", locale="en")
    rendered = render_rewrite_text(changed)
    assert "Applied 1 safe fix" in rendered
    assert "EN-LANG-004" in rendered

    blocked = replace(changed, blocked=True)
    assert "BLOCKED" in render_rewrite_text(blocked)


def test_render_empty_rules() -> None:
    assert render_rules_text([]) == "No rules match this filter."


def test_sarif_for_stdin_and_file() -> None:
    reports = [
        Analyzer().audit("In conclusion, stop.", locale="en", source="<stdin>"),
        Analyzer().audit("Таким образом, стоп.", locale="ru", source="draft.md"),
    ]
    payload = json.loads(reports_sarif(reports))
    results = payload["runs"][0]["results"]
    assert {item["ruleId"] for item in results} >= {"EN-RHET-003", "RU-RHET-004"}


def test_verification_json_failure() -> None:
    report = VerificationReport(False, [], [], 1, 2)
    assert json.loads(verification_json(report))["ok"] is False
