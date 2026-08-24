import json
from pathlib import Path

from scripts.benchmark_real_world import DEFAULT_MANIFEST, DEFAULT_RESULTS, build_results

ROOT = Path(__file__).resolve().parents[1]


def test_real_world_benchmark_seed_metrics() -> None:
    payload = build_results(DEFAULT_MANIFEST)
    summary = payload["summary"]
    sample = payload["samples"][0]

    assert summary == {
        "samples": 1,
        "source_words": 348,
        "rewrite_words": 251,
        "word_reduction": 97,
        "compression_ratio": 0.7213,
        "source_findings": 5,
        "rewrite_findings": 0,
        "finding_reduction": 5,
        "finding_reduction_rate": 1.0,
        "fact_guard_passed": 1,
        "fact_guard_pass_rate": 1.0,
        "protected_facts": 8,
        "regression_checks_passed": 1,
        "regression_checks_failed": 0,
    }
    assert sample["source_rule_counts"] == {"EN-LANG-001": 4, "EN-RHET-003": 1}
    assert sample["rewrite_rule_counts"] == {}
    assert sample["fact_guard"] == {
        "ok": True,
        "protected_facts": 8,
        "lost": 0,
        "added": 0,
    }
    assert sample["passed"] is True


def test_committed_benchmark_results_are_current() -> None:
    generated = build_results(DEFAULT_MANIFEST)
    committed = json.loads(DEFAULT_RESULTS.read_text(encoding="utf-8"))
    assert committed == generated


def test_benchmark_paths_stay_inside_repository() -> None:
    manifest = DEFAULT_MANIFEST.read_text(encoding="utf-8")
    assert "../.." not in manifest
    assert (ROOT / "examples" / "real-world-ai-source.md").is_file()
