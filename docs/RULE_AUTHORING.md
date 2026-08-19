# Authoring a rule

## Start with a reader problem

A rule must identify an observable problem such as unsupported attribution, bureaucratic phrasing, unresolved placeholders, or mechanically uniform rhythm. Do not begin with “models often write this.” Begin with why a reader or editor should review it.

## Required fields

```json
{
  "id": "EN-LANG-007",
  "locale": "en",
  "name": "Example rule",
  "description": "Why the observable pattern matters.",
  "category": "language",
  "severity": "info",
  "confidence": "medium",
  "message": "What was found.",
  "suggestion": "What the author should review.",
  "detector": {
    "type": "regex",
    "patterns": ["\\bexample\\b"]
  },
  "genres": ["article", "social"],
  "excluded_genres": [],
  "min_chars": 0,
  "max_findings": 20,
  "ignore_in_quotes": true,
  "sources": ["https://example.org/source"]
}
```

IDs follow `EN-CATEGORY-001` or `RU-CATEGORY-001`. Existing IDs are not recycled.

## Confidence

- `high`: deterministic artifact or direct language error with narrow exceptions;
- `medium`: strong editorial signal with known exceptions;
- `low`: contextual structural or style signal.

Do not use `high` merely because a pattern appears frequently in generated text.

## Genre policy

Use `genres: ["*"]` only when the failure is genuinely universal. Artifact rules usually qualify. Most rhetoric and formatting rules should name genres or exclusions.

Supported built-in genres:

```text
general social email landing article docs fiction academic legal
```

## Quotes and code

Code and URLs are always masked for analysis. Quotes are masked by default. Set `ignore_in_quotes: false` only for artifacts that remain invalid even when quoted, such as a leaked tool-call identifier.

## Safe autofix

An autofix is allowed only when the replacement is meaning-preserving across supported genres.

```json
"autofix": {
  "safe": true,
  "replacements": [
    { "pattern": "\\bin order to\\b", "replacement": "to" }
  ]
}
```

Requirements:

- no new facts;
- no deletion of a claim;
- no required syntactic restructuring outside the match;
- no reliance on a model;
- capitalization-safe behavior;
- idempotence test;
- Fact Guard pass.

A suggestion is not an autofix. Most good editorial advice should remain manual.

## Structural detectors

Available detector types are documented by the generated catalog and JSON Schema. Structural rules need:

- a meaningful `min_chars`;
- minimum sample counts;
- conservative thresholds;
- genre limits;
- an eval case close to the threshold;
- a clean case that resembles the pattern.

## Provenance

Sources explain why the pattern was considered, not why every occurrence is wrong. Link to primary research, a maintained public catalog, a style guide, or a reproducible issue.

When adapting licensed text or code, record the applicable license and attribution in `THIRD_PARTY_NOTICES.md`.
