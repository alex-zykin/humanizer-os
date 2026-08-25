#!/usr/bin/env python3
from __future__ import annotations

import json
import pprint
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmarks" / "real-world-v1"
CANDIDATES = BENCHMARK / "candidates"
SAMPLES = BENCHMARK / "samples"
MANIFEST = BENCHMARK / "manifest.jsonl"
RESULTS = BENCHMARK / "results.json"
SELECTED = (
    "human-detectors-gpt-4o-record-46",
    "human-detectors-paraphrased-gpt-4o-record-52",
    "human-detectors-paraphrased-gpt-4o-record-35",
    "human-detectors-gpt-4o-record-40",
    "human-detectors-humanized-o1-pro-record-47",
    "human-detectors-claude-record-0",
    "human-detectors-o1-pro-record-46",
    "human-detectors-claude-record-27",
    "human-detectors-paraphrased-gpt-4o-record-50",
)


class FinalizeError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalizeError(f"expected a JSON object in {path.relative_to(ROOT)}")
    return value


def _annotation_signals(metadata: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    seen: set[str] = set()
    annotations = metadata.get("annotations", [])
    if not isinstance(annotations, list):
        return ["No free-form annotation comment was released for this record."]
    for row in annotations:
        if not isinstance(row, dict):
            continue
        comment = " ".join(str(row.get("comment", "")).split())
        if not comment:
            continue
        first = re.split(r"(?<=[.!?])\s+", comment, maxsplit=1)[0]
        first = textwrap.shorten(first, width=180, placeholder="…")
        key = first.casefold()
        if key not in seen:
            signals.append(first)
            seen.add(key)
        if len(signals) == 3:
            break
    return signals or ["No free-form annotation comment was released for this record."]


def _seed_manifest_row() -> dict[str, Any]:
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise FinalizeError("seed manifest record is not a JSON object")
            return row
    raise FinalizeError("benchmark manifest is empty")


def _copy_candidate(sample_id: str) -> dict[str, Any]:
    source_dir = CANDIDATES / sample_id
    target_dir = SAMPLES / sample_id
    if not source_dir.is_dir():
        raise FinalizeError(f"candidate directory is missing: {sample_id}")
    target_dir.mkdir()
    for source_name, target_name in (
        ("source.md", "source.md"),
        ("rewrite.md", "rewrite.md"),
        ("provenance.md", "provenance.md"),
        ("metadata.json", "metadata.json"),
        ("annotations.md", "annotations.md"),
        ("audit.json", "source-audit.json"),
        ("rewrite-audit.json", "rewrite-audit.json"),
    ):
        source_path = source_dir / source_name
        if not source_path.is_file():
            raise FinalizeError(f"missing {source_name} for {sample_id}")
        shutil.copy2(source_path, target_dir / target_name)

    metadata = _read_json(source_dir / "metadata.json")
    audit = _read_json(source_dir / "rewrite-audit.json")
    fact_guard = audit.get("fact_guard")
    source_counts = audit.get("source_rule_counts")
    rewrite_counts = audit.get("rewrite_rule_counts")
    if not isinstance(fact_guard, dict):
        raise FinalizeError(f"invalid Fact Guard result for {sample_id}")
    if not isinstance(source_counts, dict) or not isinstance(rewrite_counts, dict):
        raise FinalizeError(f"invalid rule counts for {sample_id}")

    return {
        "id": sample_id,
        "locale": "en",
        "genre": "article",
        "source_path": str((target_dir / "source.md").relative_to(ROOT)),
        "rewrite_path": str((target_dir / "rewrite.md").relative_to(ROOT)),
        "provenance_path": str((target_dir / "provenance.md").relative_to(ROOT)),
        "ground_truth": str(metadata["ground_truth"]),
        "model": str(metadata["model"]),
        "license": "MIT",
        "human_annotation_signals": _annotation_signals(metadata),
        "expected": {
            "source_rule_counts": source_counts,
            "rewrite_findings": sum(int(value) for value in rewrite_counts.values()),
            "protected_facts": int(fact_guard["protected_facts"]),
            "verification_ok": bool(fact_guard["ok"]),
        },
    }


def promote_samples() -> None:
    if not CANDIDATES.is_dir():
        raise FinalizeError("candidate directory is missing")
    if SAMPLES.exists():
        shutil.rmtree(SAMPLES)
    SAMPLES.mkdir(parents=True)

    rows = [_seed_manifest_row()]
    rows.extend(_copy_candidate(sample_id) for sample_id in SELECTED)
    MANIFEST.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    shutil.rmtree(CANDIDATES)

    runner = ROOT / "scripts" / "benchmark_real_world.py"
    text = runner.read_text(encoding="utf-8")
    old = '"status": "seed",'
    new = '"status": "pilot" if len(samples) >= 10 else "seed",'
    if text.count(old) != 1:
        raise FinalizeError("benchmark status marker changed")
    runner.write_text(text.replace(old, new), encoding="utf-8")


def regenerate_results() -> dict[str, Any]:
    subprocess.run(
        [sys.executable, "scripts/benchmark_real_world.py", "--write"],
        cwd=ROOT,
        check=True,
    )
    payload = _read_json(RESULTS)
    summary = payload.get("summary")
    samples = payload.get("samples")
    if payload.get("status") != "pilot":
        raise FinalizeError("benchmark status is not pilot")
    if not isinstance(summary, dict) or not isinstance(samples, list):
        raise FinalizeError("generated benchmark result has an invalid shape")
    expected = {
        "samples": 10,
        "rewrite_findings": 0,
        "fact_guard_passed": 10,
        "regression_checks_failed": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise FinalizeError(f"unexpected summary value for {key}: {summary.get(key)!r}")
    return payload


def _sample_table(samples: list[dict[str, Any]]) -> str:
    lines = [
        "| Sample | Model | Words | Findings | Protected facts |",
        "|---|---|---:|---:|---:|",
    ]
    for row in samples:
        fact_guard = row["fact_guard"]
        lines.append(
            f"| `{row['id']}` | `{row['model']}` | "
            f"{row['source_words']} → {row['rewrite_words']} | "
            f"{row['source_findings']} → {row['rewrite_findings']} | "
            f"{fact_guard['protected_facts']} |"
        )
    return "\n".join(lines)


def _unchanged_clean_count(samples: list[dict[str, Any]]) -> int:
    count = 0
    for row in samples:
        if row["source_findings"]:
            continue
        source = (ROOT / row["source_path"]).read_text(encoding="utf-8")
        rewrite = (ROOT / row["rewrite_path"]).read_text(encoding="utf-8")
        count += source == rewrite
    return count


def _benchmark_readme(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    model_count: int,
    unchanged_clean: int,
) -> str:
    table = _sample_table(samples)
    return f"""# Real-world benchmark v1

This benchmark turns provenance-tracked machine-generated samples into a reproducible HumanizerOS evaluation.

## Status

The committed baseline is a **10-sample pilot**. It covers {model_count} generation modes from the MIT-licensed Human Detectors dataset across varied article sections. The pilot is large enough to exercise the workflow, but it is not a representative corpus and does not support a global humanization score.

## Pilot baseline

| Metric | Current result |
|---|---:|
| Samples | {summary['samples']} |
| Generation modes | {model_count} |
| Source words | {summary['source_words']} |
| Rewrite words | {summary['rewrite_words']} |
| Findings | {summary['source_findings']} → {summary['rewrite_findings']} |
| Protected facts checked | {summary['protected_facts']} |
| Fact Guard passes | {summary['fact_guard_passed']}/{summary['samples']} |
| Regression checks | {summary['regression_checks_passed']}/{summary['samples']} |

{unchanged_clean} clean source texts produced no deterministic findings and were left unchanged. This is intentional: HumanizerOS should not rewrite effective prose merely to make it different.

## Sample coverage

{table}

The model labels include post-processed variants exactly as released by the source dataset. They describe generation provenance, not a claim that each variant has the same editing history.

## What it measures

For every sample, the runner records source and rewrite word counts, findings before and after editing, per-rule counts, Fact Guard status, protected-item counts, declared regression checks, generation provenance, and human annotation signals.

The benchmark does not calculate an AI-authorship probability. Fact Guard checks consistency between source and rewrite; it does not certify that generated claims are true.

## Run it

```bash
python scripts/benchmark_real_world.py
python scripts/benchmark_real_world.py --json
python scripts/benchmark_real_world.py --check
```

Regenerate the committed result only after an intentional engine or corpus change:

```bash
python scripts/benchmark_real_world.py --write
```

CI runs `--check`, so rule changes and fact-extraction changes cannot silently invalidate the baseline.

## Layout

- [`manifest.jsonl`](manifest.jsonl) stores one provenance and expectation record per sample.
- [`results.json`](results.json) is generated by the current engine.
- [`samples/`](samples/) contains each redistributed machine-generated source, its conservative rewrite, provenance, annotations, and source/rewrite audits.
- The original seed demo remains in [`../../examples/`](../../examples/).

## Adding a sample

A contribution needs redistribution permission, an explicit ground-truth label, generation-model metadata when available, a provenance file, an independently authored rewrite, retained human annotation signals, expected rule counts, and Fact Guard values. Do not copy a paired human reference article unless its license clearly permits redistribution.

The v1 target remains 30–50 samples. Expansion should increase model and genre coverage, add clean and adversarial boundaries, and include blind reader evaluation before publishing quality claims.
"""


def update_benchmark_readme(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    model_count: int,
    unchanged_clean: int,
) -> None:
    content = _benchmark_readme(summary, samples, model_count, unchanged_clean)
    (BENCHMARK / "README.md").write_text(content, encoding="utf-8")


def update_main_readme(
    summary: dict[str, Any], model_count: int, unchanged_clean: int
) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    old_nav = "[Real-world sample](#real-world-ai-sample) · [Claude and Codex]"
    new_nav = (
        "[Real-world sample](#real-world-ai-sample) · "
        "[Benchmark](#ten-sample-real-world-pilot) · [Claude and Codex]"
    )
    if old_nav not in text:
        raise FinalizeError("README navigation marker changed")
    text = text.replace(old_nav, new_nav, 1)

    marker = (
        "Fact Guard checks consistency between source and revision. It does not certify "
        "that a generated claim or quotation is true.\n\n## Why HumanizerOS"
    )
    section = f"""Fact Guard checks consistency between source and revision. It does not certify that a generated claim or quotation is true.

## Ten-sample real-world pilot

The committed [`Real-World Benchmark v1`](benchmarks/real-world-v1/) now contains {summary['samples']} provenance-tracked machine-generated samples across {model_count} generation modes. The current deterministic baseline is:

| Metric | Result |
|---|---:|
| Source findings | {summary['source_findings']} |
| Rewrite findings | {summary['rewrite_findings']} |
| Protected facts checked | {summary['protected_facts']} |
| Fact Guard passes | {summary['fact_guard_passed']}/{summary['samples']} |

{unchanged_clean} clean sources were left unchanged. The pilot validates the evaluation pipeline; it does not claim authorship detection or universal writing quality.

## Why HumanizerOS"""
    if marker not in text:
        raise FinalizeError("README insertion marker changed")
    path.write_text(text.replace(marker, section, 1), encoding="utf-8")


def update_changelog(summary: dict[str, Any], model_count: int) -> None:
    path = ROOT / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    item = (
        f"- A {summary['samples']}-sample Real-World Benchmark v1 pilot across "
        f"{model_count} Human Detectors generation modes, with verified rewrites, "
        f"{summary['protected_facts']} protected facts, and clean-text "
        "non-disturbance cases.\n"
    )
    if item in text:
        return
    marker = "## [Unreleased]\n\n"
    if marker not in text:
        raise FinalizeError("CHANGELOG Unreleased marker changed")
    path.write_text(
        text.replace(marker, marker + "### Added\n\n" + item + "\n", 1),
        encoding="utf-8",
    )


def update_evaluation(summary: dict[str, Any], model_count: int) -> None:
    path = ROOT / "docs" / "EVALUATION.md"
    text = path.read_text(encoding="utf-8")
    if "## Real-world pilot" in text:
        return
    marker = "## Current limits"
    if marker not in text:
        raise FinalizeError("evaluation limits marker changed")
    section = f"""## Real-world pilot

The committed pilot contains {summary['samples']} provenance-tracked machine-generated samples across {model_count} released generation modes. It records {summary['source_findings']} source findings, {summary['rewrite_findings']} rewrite findings, and {summary['protected_facts']} protected facts with {summary['fact_guard_passed']}/{summary['samples']} Fact Guard passes.

Run `python scripts/benchmark_real_world.py --check` to verify that the manifest, rewrites, and committed result still match the current engine. The pilot is a regression and preservation benchmark, not an authorship detector or a representative quality study.

"""
    path.write_text(text.replace(marker, section + marker, 1), encoding="utf-8")


def update_regression_test(summary: dict[str, Any]) -> None:
    expected = pprint.pformat(summary, sort_dicts=False, width=88)
    content = f'''import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmark_real_world import (  # noqa: E402
    DEFAULT_MANIFEST,
    DEFAULT_RESULTS,
    build_results,
)

EXPECTED_SUMMARY = {expected}


def test_real_world_benchmark_pilot_metrics() -> None:
    payload = build_results(DEFAULT_MANIFEST)
    assert payload["status"] == "pilot"
    assert payload["summary"] == EXPECTED_SUMMARY
    assert len(payload["samples"]) == 10
    assert all(sample["passed"] for sample in payload["samples"])
    assert all(not sample["rewrite_rule_counts"] for sample in payload["samples"])

    seed = next(
        sample
        for sample in payload["samples"]
        if sample["id"] == "human-detectors-dinosaur-gpt4o"
    )
    assert seed["source_rule_counts"] == {{"EN-LANG-001": 4, "EN-RHET-003": 1}}
    assert seed["fact_guard"]["protected_facts"] == 8


def test_committed_benchmark_results_are_current() -> None:
    generated = build_results(DEFAULT_MANIFEST)
    committed = json.loads(DEFAULT_RESULTS.read_text(encoding="utf-8"))
    assert committed == generated


def test_benchmark_paths_stay_inside_repository() -> None:
    manifest = DEFAULT_MANIFEST.read_text(encoding="utf-8")
    assert "../.." not in manifest
    assert (ROOT / "examples" / "real-world-ai-source.md").is_file()
    samples = ROOT / "benchmarks" / "real-world-v1" / "samples"
    assert samples.is_dir()
    assert len([path for path in samples.iterdir() if path.is_dir()]) == 9
    assert not (ROOT / "benchmarks" / "real-world-v1" / "candidates").exists()
'''
    (ROOT / "tests" / "test_real_world_benchmark.py").write_text(
        content,
        encoding="utf-8",
    )


def update_docs_and_tests(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    raw_samples = payload["samples"]
    if not isinstance(summary, dict) or not isinstance(raw_samples, list):
        raise FinalizeError("benchmark result has an invalid shape")
    samples = [row for row in raw_samples if isinstance(row, dict)]
    if len(samples) != len(raw_samples):
        raise FinalizeError("benchmark sample result contains a non-object")
    models = {str(row["model"]) for row in samples}
    model_count = len(models)
    unchanged_clean = _unchanged_clean_count(samples)
    update_benchmark_readme(summary, samples, model_count, unchanged_clean)
    update_main_readme(summary, model_count, unchanged_clean)
    update_changelog(summary, model_count)
    update_evaluation(summary, model_count)
    update_regression_test(summary)


def main() -> int:
    try:
        promote_samples()
        payload = regenerate_results()
        update_docs_and_tests(payload)
    except (FinalizeError, OSError, KeyError, ValueError) as exc:
        print(f"finalize benchmark: {exc}", file=sys.stderr)
        return 2
    print("Prepared the ten-sample Real-World Benchmark v1 pilot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
