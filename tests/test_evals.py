import json
from pathlib import Path

import pytest

from humanizer_os.analyzer import Analyzer

ROOT = Path(__file__).resolve().parents[1]


def load_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for locale in ("en", "ru"):
        path = ROOT / "evals" / locale / "cases.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            case = json.loads(line)
            case["locale"] = locale
            cases.append(case)
    return cases


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: str(case["id"]))
def test_eval_case(case: dict[str, object]) -> None:
    report = Analyzer().audit(
        str(case["text"]),
        locale=str(case["locale"]),
        genre=str(case.get("genre", "general")),
    )
    found = {item.rule_id for item in report.findings}
    expected = set(case.get("expect", []))
    forbidden = set(case.get("forbid", []))
    assert expected <= found, f"missing {expected - found}; found={found}"
    assert not (forbidden & found), f"forbidden {forbidden & found}; found={found}"
    if case.get("clean"):
        assert not found, f"expected a clean text, found={found}"
