# HumanizerOS roadmap

The roadmap is directional, not a promise of dates.

## 0.2 — stronger deterministic core

- section-aware Markdown analysis;
- project configuration and rule overrides;
- baseline files for gradual CI adoption;
- morphology-assisted Russian checks behind an optional extra;
- reusable GitHub Action;
- editor-friendly compact JSON lines;
- extension API for external language packs;
- signed provenance metadata;
- large-file limits and performance benchmarks;
- Python 3.15 preview CI when runners support it.

### Expressive RU, deterministic foundation

- opt-in install extra;
- detect and preserve existing profanity;
- classify function, intensity, and target;
- normalize obvious repetitions and malformed forms;
- mask expressions for platform presets;
- independently authored data with per-entry provenance;
- no vendoring of the unlicensed `russian-swears` corpus.

## 0.3 — voice and semantic rewriting

- HumanizerOS Voice with explicit author samples;
- provider-neutral rewrite interface;
- local and hosted adapters as separate extras;
- reviewable multi-variant output;
- Fact Guard and second-audit gates on provider output;
- privacy and retention disclosure per provider;
- offline mode;
- expressive modes: `preserve`, `normalize`, `add`, and `censor`;
- `add` available only by explicit request and bounded by targeting policy.

## 0.4 — integrations

- VS Code extension;
- GitHub Action and pull-request annotations;
- pre-commit integration;
- batch API;
- Creator Content OS adapter;
- WordPress and Markdown-editor integrations;
- rule-pack registry prototype.

## 0.5 — HumanizerOS Studio

- visual source/revision/diff review;
- per-finding accept/reject;
- voice and genre profiles;
- team policy and baselines;
- provider controls and explicit network boundary;
- export to Markdown, JSON, SARIF, and Content OS.

## 1.0 — stable platform

- stable extension and compatibility policy;
- measured false-positive budgets by language and genre;
- blinded reader evaluation for semantic rewrites;
- signed release artifacts and documented supply chain;
- mature privacy controls;
- public benchmark methodology and reproducible reports;
- at least one independently maintained external language pack.

## Research track

A separate experimental track may adapt StoryScope-inspired discourse analysis to long English fiction and later to validated Russian corpora. It will not silently influence short-form business or social text.
