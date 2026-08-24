# Changelog

All notable changes are documented here. The project follows Semantic Versioning.

## [Unreleased]

### Added

- Real-World Benchmark v1 seed framework with a versioned manifest, deterministic results, provenance fields, regression checks, CI integration, and a reproducible command-line runner.

### Planned

- Expand Real-World Benchmark v1 to 30–50 provenance-tracked samples across topics, genres, and generation models.
- Expressive RU foundation for opt-in detection, preservation, normalization, and censorship.
- Optional LLM adapters with provider-neutral interfaces and local Fact Guard verification.
- Author voice matching with explicit sample consent.
- HumanizerOS Studio and plugin packages for editors and content systems.

## [0.1.1] - 2026-08-25

### Added

- A provenance-tracked long-form demo from the MIT-licensed Human Detectors dataset, using a released `gpt-4o` sample labeled `AI-generated` and a HumanizerOS-authored rewrite.
- Regression coverage for the real-world demo, blockquotes containing nested direct quotations, Markdown/HTML README markup, and local repeated-opening clusters.
- Two English eval cases grounded in the real-world sample, including a clean counterexample for `groundbreaking ceremony`.

### Changed

- Repositioned HumanizerOS as an English-first product with Russian available as an optional language-native locale.
- Promoted the root `SKILL.md` as the canonical Agent Skill and added one-command installation examples for Claude Code and Codex through `npx skills`.
- Reworked the main README around reproducible before/after evidence, real-world material, and Fact Guard.
- Expanded `EN-LANG-001` with inflated-significance patterns surfaced by the real-world sample and its human annotations.
- Extended Fact Guard to preserve direct quotations while allowing straight/curly quote typography changes.
- Reduced proper-name false positives from sentence scaffolding such as `As Dr.`.
- Made structural repeated-opening checks local rather than document-global and taught them to ignore common Markdown/HTML presentation lines.
- Protected complete Markdown blockquotes before nested quotation marks are scanned, so attributed source excerpts remain outside normal prose linting.

### Quality

- 175 automated tests pass with 92.14% branch-aware coverage.
- 59 bilingual eval cases pass at 100%.
- Ruff, mypy, documentation checks, self-audit, wheel/sdist builds, and clean-environment smoke tests pass in CI.

## [0.1.0] - 2026-08-19

### Added

- HumanizerOS platform identity and naming contract for the core, language packs, skills, providers, Voice, Expressive RU, and Studio.
- Repository branding assets, bilingual project documentation, and a terminal walkthrough for the public launch.
- Dependency-free Python core and CLI.
- Separate English and Russian rule packs.
- 65 explainable rules across artifacts, language, rhetoric, formatting, content, and structure.
- Genre profiles for general, social, email, landing, article, docs, fiction, academic, and legal text.
- Fact Guard for dates, numbers, money, versions, UUIDs, commit hashes, URLs, email addresses, handles, proper names, and code.
- Safe deterministic fixes with post-rewrite fact verification and atomic in-place writes.
- Text, versioned JSON, JSON Schema, and SARIF audit output.
- Voice-profile measurements without identity inference.
- 57 bilingual eval cases and 164 automated tests with a 90% coverage gate.
- Agent Skills for automatic, English, and Russian workflows.

[Unreleased]: https://github.com/alex-zykin/humanizer-os/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/alex-zykin/humanizer-os/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/alex-zykin/humanizer-os/releases/tag/v0.1.0
