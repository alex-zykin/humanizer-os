# HumanizerOS architecture

## Platform principle

HumanizerOS is a shared runtime and contract system for language packs, author profiles, expression modules, model providers, agent skills, and product integrations. The deterministic core stays independently useful. Optional modules may add capabilities but may not weaken fact preservation, explainability, or explicit network consent.

## Goals

- local-first and dependency-free runtime;
- explainable findings with stable IDs;
- independent language packs;
- protected facts and code;
- deterministic behavior suitable for CI;
- optional future model providers behind a separate interface.

## Package map

```text
src/humanizer_os/
├── _version.py      package version
├── analyzer.py      orchestration and metrics
├── cli.py           command-line interface and exit codes
├── detectors.py     regex and structural detectors
├── facts.py         protected fact extraction and comparison
├── fixes.py         safe replacement matching and case handling
├── language.py      language resolution
├── models.py        public dataclasses
├── output.py        text, JSON, and SARIF renderers
├── profiles.py      observable voice measurements
├── registry.py      rule loading and validation
├── rewriter.py      fact-guarded rewrite orchestration
├── text.py          offset-preserving text utilities
├── verify.py        public verification facade
└── data/rules/      English and Russian catalogs
```

## Data flow

### Audit

```text
input
  ├─> language resolver
  ├─> protected span finder
  └─> rule registry(language, genre, length)
          └─> detectors(masked text)
                  └─> findings(original offsets)
                          └─> text / JSON / SARIF
```

Masking replaces protected characters with spaces while retaining newlines and string length. Detector offsets therefore map directly to the original text.

### Safe fix

```text
input
  ├─> audit before
  ├─> extract facts + protected spans
  ├─> collect safe replacement candidates
  ├─> resolve overlaps
  ├─> apply from right to left
  ├─> verify facts
  │      ├─ fail -> restore original
  │      └─ pass -> keep revised text
  └─> audit after + change list
```

## Public API

The intended stable entry points are:

```python
from humanizer_os import Analyzer, Rewriter, verify_texts
```

Returned dataclasses expose `to_dict()` for serialization. Native JSON envelopes are documented in [JSON_API.md](JSON_API.md). Internal detector APIs may evolve before 1.0.

## Rule registry

Rule packs are UTF-8 JSON bundled as package data. Runtime validation checks:

- unique IDs;
- supported locale, severity, confidence, and detector type;
- valid regular expressions;
- valid safe-fix expressions.

The JSON Schema in `schemas/rule.schema.json` supports editor tooling and future external packs. Core validation remains dependency-free.

## Detector extension points

A detector receives a `Rule` and an offset-preserving text string and returns spans. New detectors are registered in `DETECTORS`.

A detector must:

- be deterministic;
- return original-compatible offsets;
- enforce minimum evidence through rule parameters;
- avoid network access;
- have positive and clean eval cases;
- document complexity for long files.

## File-system behavior

- `audit` can read files, directories, or stdin.
- directory traversal includes common prose extensions and ignores build/vendor directories.
- `fix --write` writes only explicitly named files; directories are rejected.
- stdin cannot be combined with `--write`.
- encoding is UTF-8 and existing LF/CRLF line endings are preserved.
- writes use a same-directory temporary file, `fsync`, mode preservation, and atomic replacement.
- symbolic links are refused for in-place writes.
- repeated or overlapping file inputs are de-duplicated by resolved path.

Backups are intentionally left to version control or the caller; HumanizerOS does not create silent sidecar files.

## Platform modules

The core remains usable without these optional layers:

- **HumanizerOS Voice** — consented author-sample comparison and voice constraints;
- **Expressive RU** — opt-in Russian expression handling with provenance and targeting controls;
- **HumanizerOS Providers** — provider-neutral semantic rewrite adapters with explicit network disclosure;
- **HumanizerOS Studio** — visual review, diff, policy, and team workflows;
- morphology adapters for Russian;
- section-aware structural analysis;
- editor protocol and language-server integration;
- Creator Content OS integration;
- third-party rule packs with signed metadata.
