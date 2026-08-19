#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from humanizer_os.analyzer import Analyzer  # noqa: E402


def load_cases(locale: str) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    path = ROOT / "evals" / locale / "cases.jsonl"
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        case = json.loads(line)
        case["locale"] = locale
        case["line_number"] = line_number
        cases.append(case)
    return cases


def evaluate(locales: list[str]) -> dict[str, object]:
    analyzer = Analyzer()
    rows: list[dict[str, object]] = []
    counts = Counter()

    for locale in locales:
        for case in load_cases(locale):
            report = analyzer.audit(
                str(case["text"]),
                locale=locale,
                genre=str(case.get("genre", "general")),
            )
            found = {item.rule_id for item in report.findings}
            expected = set(case.get("expect", []))
            forbidden = set(case.get("forbid", []))
            missing = sorted(expected - found)
            unexpected = sorted(forbidden & found)
            if case.get("clean"):
                unexpected = sorted(found)
            passed = not missing and not unexpected
            counts["passed" if passed else "failed"] += 1
            counts[f"{locale}_total"] += 1
            rows.append(
                {
                    "id": case["id"],
                    "locale": locale,
                    "genre": case.get("genre", "general"),
                    "passed": passed,
                    "missing": missing,
                    "unexpected": unexpected,
                    "found": sorted(found),
                }
            )

    total = counts["passed"] + counts["failed"]
    return {
        "summary": {
            "total": total,
            "passed": counts["passed"],
            "failed": counts["failed"],
            "pass_rate": round(counts["passed"] / max(total, 1), 4),
            "by_locale": {locale: counts[f"{locale}_total"] for locale in locales},
        },
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run HumanizerOS's bilingual eval suite.")
    parser.add_argument("--locale", choices=("all", "en", "ru"), default="all")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    locales = ["en", "ru"] if args.locale == "all" else [args.locale]
    result = evaluate(locales)

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        summary = result["summary"]
        print(
            f"Eval: {summary['passed']}/{summary['total']} passed "
            f"({summary['pass_rate'] * 100:.1f}%)"
        )
        for case in result["cases"]:
            if not case["passed"]:
                print(
                    f"FAIL {case['id']}: missing={case['missing']} "
                    f"unexpected={case['unexpected']} found={case['found']}"
                )
    return 1 if result["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
