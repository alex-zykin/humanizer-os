# Evaluation

## Current suite

Eval cases live in:

```text
evals/en/cases.jsonl
evals/ru/cases.jsonl
```

Each line is a self-contained JSON object:

```json
{
  "id": "en-filler",
  "genre": "email",
  "text": "In order to approve it, reply before Friday.",
  "expect": ["EN-LANG-004"]
}
```

A clean case uses:

```json
{
  "id": "en-clean-email",
  "genre": "email",
  "text": "The invoice is attached. Please send payment by 14 August 2026.",
  "clean": true
}
```

A boundary case can forbid one rule while allowing unrelated findings:

```json
{
  "id": "en-quoted-formula",
  "genre": "article",
  "text": "She wrote, \"This is not just a tool, but a movement.\"",
  "forbid": ["EN-RHET-001"]
}
```

## Real-world benchmark

`benchmarks/real-world-v1/` evaluates complete, provenance-tracked AI-generated samples and their independently authored rewrites. Unlike the minimal eval fixtures, these records preserve article-length structure, quotations, attribution, and mixed signals.

The seed framework records:

- findings and per-rule counts before and after rewriting;
- word-count change;
- Fact Guard pass/fail and protected-item count;
- model, ground-truth label, and license metadata;
- human annotation signals supplied by the source dataset;
- regression expectations that prevent silent metric drift.

Run it with:

```bash
python scripts/benchmark_real_world.py
python scripts/benchmark_real_world.py --check
```

The initial one-sample result validates the framework only. It is not a representative estimate of rule recall, false-positive rate, or rewrite quality. Real-World Benchmark v1 targets 30–50 licensed samples across topics and models before aggregate claims are published.

## Commands

```bash
python scripts/evaluate.py
python scripts/benchmark_real_world.py --check
pytest --cov=humanizer_os --cov-report=term-missing
```

The eval runner requires every expected rule to appear, every forbidden rule to remain absent, and clean cases to produce no findings. Extra findings are allowed in non-clean cases so a fixture can exercise multiple rules as the catalog grows.

## Release gates

A release must pass:

- registry validation;
- unit and CLI tests;
- English and Russian eval sets;
- real-world benchmark freshness;
- fact-preservation tests;
- repeated-run idempotence;
- JSON Schema validation;
- rule catalog freshness;
- documentation links;
- wheel and source-distribution smoke tests.

`python scripts/check_release.py` also checks that runtime, package, changelog, and citation versions agree and that every built-in rule has explicit eval coverage.

## Metrics that matter

### Rule precision

Measure each rule separately. A project-wide precision score can hide a noisy rule behind several easy artifact detectors.

### Clean-text disturbance

Human text that is already effective must remain unchanged. Clean fixtures are mandatory for every new rule.

### Fact preservation

Every safe rewrite must preserve protected facts. Fact Guard is a release blocker, not a reporting metric.

### Idempotence

Running the deterministic fixer twice should produce no second-pass changes.

### Reader preference

Blind human evaluation is required before semantic rewriting is called stable. Ask whether the revised version is clearer, more natural, and faithful, not whether it can fool a detector.

## Corpus policy

Do not commit private text, scraped proprietary corpora, Books3 passages, or copied source examples without compatible licensing. A real-world benchmark record needs explicit redistribution permission, provenance, and a separately authored rewrite. Human reference articles stay out of the repository unless their license permits redistribution.

## Current limits

The built-in fixture set and one-sample benchmark seed are regression tools, not representative corpora. They do not support an authorship claim or a global humanization score. See [LIMITATIONS.md](LIMITATIONS.md).
