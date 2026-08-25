import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmark_real_world import (  # noqa: E402
    DEFAULT_MANIFEST,
    DEFAULT_RESULTS,
    build_results,
)

EXPECTED_SUMMARY = {'samples': 10,
 'source_words': 5017,
 'rewrite_words': 4822,
 'word_reduction': 195,
 'compression_ratio': 0.9611,
 'source_findings': 13,
 'rewrite_findings': 0,
 'finding_reduction': 13,
 'finding_reduction_rate': 1.0,
 'fact_guard_passed': 10,
 'fact_guard_pass_rate': 1.0,
 'protected_facts': 189,
 'regression_checks_passed': 10,
 'regression_checks_failed': 0}


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
    assert seed["source_rule_counts"] == {"EN-LANG-001": 4, "EN-RHET-003": 1}
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
