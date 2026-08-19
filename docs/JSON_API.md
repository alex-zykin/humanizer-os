# JSON and SARIF contracts

All native JSON outputs use an explicit envelope:

```json
{
  "schema_version": 1,
  "tool": {
    "name": "humanizer-os",
    "version": "0.1.0"
  },
  "command": "audit",
  "results": []
}
```

Schemas live in `schemas/`:

- `audit-output.schema.json`;
- `rewrite-output.schema.json`;
- `verification-output.schema.json`;
- `rules-output.schema.json`;
- `profile-output.schema.json`;
- `rule.schema.json`.

## Audit result

Each item includes path, language, genre, metrics, protected facts, and findings. A finding has a stable rule ID, offsets, line and column, confidence, message, suggestion, excerpt, source links, and whether a safe fix exists.

```json
{
  "path": "post.md",
  "language": "ru",
  "genre": "social",
  "metrics": {
    "characters": 642,
    "words": 104,
    "sentences": 8,
    "paragraphs": 3,
    "findings": 2,
    "findings_by_severity": {"info": 1, "warning": 1, "error": 0},
    "review_priority": 14
  },
  "facts": [],
  "findings": []
}
```

`review_priority` is a bounded triage score derived from severity and confidence. It is not an authorship probability, quality grade, or detector score.

## Rewrite result

Rewrite JSON contains `original`, `text`, `changes`, audit summaries before and after, and verification output. Consumers should inspect `verification.ok` before accepting a result. When verification fails, `text` is the original input and `blocked` is true.

## Verification result

```json
{
  "schema_version": 1,
  "tool": {"name": "humanizer-os", "version": "0.1.0"},
  "command": "verify",
  "result": {
    "ok": false,
    "missing": [],
    "added": [],
    "reason": "Protected facts changed"
  }
}
```

Fact lists are multiset-aware: repeating a protected value twice and then deleting one occurrence is reported.

## SARIF

`audit --format sarif` emits SARIF 2.1.0. It contains only diagnostics, not full source files. The GitHub upload action can ingest it:

```yaml
- run: humanizer-os audit docs/ --lang en --genre docs --format sarif > humanizer-os.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: humanizer-os.sarif
```

SARIF severity maps `error` to `error`, `warning` to `warning`, and `info` to `note`.

## Compatibility

- New optional fields may appear within schema version 1.
- Existing required fields will not be removed before a schema-major change.
- Rule IDs remain stable within a product major version.
- Human-readable text output is not a machine contract.
