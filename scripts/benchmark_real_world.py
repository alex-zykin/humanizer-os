#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from humanizer_os import Analyzer, AuditReport, verify_texts  # noqa: E402

DEFAULT_MANIFEST = ROOT / "benchmarks" / "real-world-v1" / "manifest.jsonl"
DEFAULT_RESULTS = ROOT / "benchmarks" / "real-world-v1" / "results.json"


class BenchmarkError(RuntimeError):
    pass


def _repo_path(raw: object, *, field: str, sample_id: str) -> Path:
    value = str(raw).strip()
    if not value:
        raise BenchmarkError(f"{sample_id}: {field} is empty")
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise BenchmarkError(f"{sample_id}: {field} escapes the repository root")
    if not path.is_file():
        raise BenchmarkError(f"{sample_id}: {field} does not exist: {value}")
    return path


def load_manifest(path: Path = DEFAULT_MANIFEST) -> list[dict[str, Any]]:
    if not path.is_file():
        raise BenchmarkError(f"manifest does not exist: {path}")

    samples: list[dict[str, Any]] = []
    seen: set[str] = set()
    required = {
        "id",
        "locale",
        "genre",
        "source_path",
        "rewrite_path",
        "provenance_path",
        "ground_truth",
        "model",
        "license",
        "expected",
    }

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            sample = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BenchmarkError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
        if not isinstance(sample, dict):
            raise BenchmarkError(f"{path}:{line_number}: sample must be a JSON object")

        missing = sorted(required - sample.keys())
        if missing:
            raise BenchmarkError(
                f"{path}:{line_number}: missing fields: {', '.join(missing)}"
            )
        sample_id = str(sample["id"])
        if not sample_id:
            raise BenchmarkError(f"{path}:{line_number}: sample ID is empty")
        if sample_id in seen:
            raise BenchmarkError(f"duplicate sample ID: {sample_id}")
        seen.add(sample_id)

        locale = str(sample["locale"])
        if locale not in {"en", "ru"}:
            raise BenchmarkError(f"{sample_id}: unsupported locale {locale!r}")
        if not isinstance(sample["expected"], dict):
            raise BenchmarkError(f"{sample_id}: expected must be an object")
        annotations = sample.get("human_annotation_signals", [])
        if not isinstance(annotations, list) or not all(
            isinstance(item, str) and item.strip() for item in annotations
        ):
            raise BenchmarkError(
                f"{sample_id}: human_annotation_signals must be a list of strings"
            )

        for field in ("source_path", "rewrite_path", "provenance_path"):
            _repo_path(sample[field], field=field, sample_id=sample_id)
        samples.append(sample)

    if not samples:
        raise BenchmarkError(f"manifest is empty: {path}")
    return samples


def _rule_counts(report: AuditReport) -> dict[str, int]:
    return dict(sorted(Counter(item.rule_id for item in report.findings).items()))


def _expected_rule_counts(expected: dict[str, Any], sample_id: str) -> dict[str, int]:
    raw = expected.get("source_rule_counts")
    if not isinstance(raw, dict):
        raise BenchmarkError(f"{sample_id}: expected.source_rule_counts must be an object")
    counts: dict[str, int] = {}
    for rule_id, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise BenchmarkError(
                f"{sample_id}: expected count for {rule_id!r} must be a non-negative integer"
            )
        counts[str(rule_id)] = value
    return dict(sorted(counts.items()))


def evaluate_sample(sample: dict[str, Any], analyzer: Analyzer) -> dict[str, Any]:
    sample_id = str(sample["id"])
    source_path = _repo_path(sample["source_path"], field="source_path", sample_id=sample_id)
    rewrite_path = _repo_path(
        sample["rewrite_path"], field="rewrite_path", sample_id=sample_id
    )
    source_text = source_path.read_text(encoding="utf-8")
    rewrite_text = rewrite_path.read_text(encoding="utf-8")
    locale = str(sample["locale"])
    genre = str(sample["genre"])

    source_report = analyzer.audit(source_text, locale=locale, genre=genre)
    rewrite_report = analyzer.audit(rewrite_text, locale=locale, genre=genre)
    verification = verify_texts(source_text, rewrite_text)

    source_rule_counts = _rule_counts(source_report)
    rewrite_rule_counts = _rule_counts(rewrite_report)
    source_words = int(source_report.metrics["words"])
    rewrite_words = int(rewrite_report.metrics["words"])
    source_findings = len(source_report.findings)
    rewrite_findings = len(rewrite_report.findings)
    expected = sample["expected"]
    expected_rule_counts = _expected_rule_counts(expected, sample_id)

    checks = {
        "source_rule_counts": source_rule_counts == expected_rule_counts,
        "rewrite_findings": rewrite_findings == int(expected.get("rewrite_findings", 0)),
        "protected_facts": verification.original_count
        == int(expected.get("protected_facts", verification.original_count)),
        "verification_ok": verification.ok
        is bool(expected.get("verification_ok", True)),
    }

    return {
        "id": sample_id,
        "locale": locale,
        "genre": genre,
        "ground_truth": str(sample["ground_truth"]),
        "model": str(sample["model"]),
        "license": str(sample["license"]),
        "source_path": str(sample["source_path"]),
        "rewrite_path": str(sample["rewrite_path"]),
        "provenance_path": str(sample["provenance_path"]),
        "human_annotation_signals": list(sample.get("human_annotation_signals", [])),
        "source_words": source_words,
        "rewrite_words": rewrite_words,
        "word_reduction": source_words - rewrite_words,
        "compression_ratio": round(rewrite_words / max(source_words, 1), 4),
        "source_findings": source_findings,
        "rewrite_findings": rewrite_findings,
        "finding_reduction": source_findings - rewrite_findings,
        "source_rule_counts": source_rule_counts,
        "rewrite_rule_counts": rewrite_rule_counts,
        "fact_guard": {
            "ok": verification.ok,
            "protected_facts": verification.original_count,
            "lost": len(verification.lost),
            "added": len(verification.added),
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def build_results(manifest: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    analyzer = Analyzer()
    samples = [evaluate_sample(sample, analyzer) for sample in load_manifest(manifest)]

    source_words = sum(int(sample["source_words"]) for sample in samples)
    rewrite_words = sum(int(sample["rewrite_words"]) for sample in samples)
    source_findings = sum(int(sample["source_findings"]) for sample in samples)
    rewrite_findings = sum(int(sample["rewrite_findings"]) for sample in samples)
    fact_guard_passed = sum(bool(sample["fact_guard"]["ok"]) for sample in samples)
    checks_passed = sum(bool(sample["passed"]) for sample in samples)

    return {
        "schema_version": 1,
        "benchmark": "real-world-v1",
        "status": "pilot" if len(samples) >= 10 else "seed",
        "summary": {
            "samples": len(samples),
            "source_words": source_words,
            "rewrite_words": rewrite_words,
            "word_reduction": source_words - rewrite_words,
            "compression_ratio": round(rewrite_words / max(source_words, 1), 4),
            "source_findings": source_findings,
            "rewrite_findings": rewrite_findings,
            "finding_reduction": source_findings - rewrite_findings,
            "finding_reduction_rate": round(
                (source_findings - rewrite_findings) / max(source_findings, 1), 4
            ),
            "fact_guard_passed": fact_guard_passed,
            "fact_guard_pass_rate": round(fact_guard_passed / len(samples), 4),
            "protected_facts": sum(
                int(sample["fact_guard"]["protected_facts"]) for sample in samples
            ),
            "regression_checks_passed": checks_passed,
            "regression_checks_failed": len(samples) - checks_passed,
        },
        "samples": samples,
    }


def serialize(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _print_summary(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    print(
        "Real-World Benchmark v1: "
        f"{summary['samples']} sample(s), "
        f"{summary['source_findings']} → {summary['rewrite_findings']} findings, "
        f"Fact Guard {summary['fact_guard_passed']}/{summary['samples']}, "
        f"checks {summary['regression_checks_passed']}/{summary['samples']}"
    )
    for sample in payload["samples"]:
        if not sample["passed"]:
            failed = [name for name, passed in sample["checks"].items() if not passed]
            print(f"FAIL {sample['id']}: {', '.join(failed)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the provenance-tracked HumanizerOS real-world benchmark."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Rewrite the committed results file.")
    mode.add_argument("--check", action="store_true", help="Fail when results are stale.")
    args = parser.parse_args()

    try:
        payload = build_results(args.manifest)
    except BenchmarkError as exc:
        print(f"benchmark: {exc}", file=sys.stderr)
        return 2

    rendered = serialize(payload)
    if args.write:
        args.results.parent.mkdir(parents=True, exist_ok=True)
        args.results.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.results}")
    elif args.check:
        if not args.results.is_file():
            print(f"benchmark results are missing: {args.results}", file=sys.stderr)
            return 1
        committed = args.results.read_text(encoding="utf-8")
        if committed != rendered:
            diff = difflib.unified_diff(
                committed.splitlines(),
                rendered.splitlines(),
                fromfile=str(args.results),
                tofile="generated benchmark results",
                lineterm="",
            )
            print("\n".join(diff), file=sys.stderr)
            return 1
        print("Real-World Benchmark v1 results are up to date")

    if args.as_json:
        print(rendered, end="")
    elif not args.write and not args.check:
        _print_summary(payload)

    failed = int(payload["summary"]["regression_checks_failed"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
