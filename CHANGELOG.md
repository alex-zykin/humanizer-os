# Changelog

All notable changes are documented here. The project follows Semantic Versioning.

## [Unreleased]

### Changed

- Repositioned HumanizerOS as an English-first product with Russian available as an optional language-native locale.
- Reworked the main README around outcome, reproducible verified rewrites, Agent Skill installation, and Fact Guard rather than multilingual implementation details.
- Promoted `SKILL.md` at the repository root as the canonical default Agent Skill for the open skills ecosystem.
- Expanded the standalone root Skill with an English review map so it remains useful when the CLI is unavailable.
- Added one-command installation examples for Claude Code and Codex through `npx skills`.
- Removed the duplicate nested default skill so the canonical `humanizer-os` skill has a single discovery target.
- Added a regression-tested product-launch demo with 10 findings across 8 rules and 6 protected facts preserved.
- Added a real-world long-form demo from the MIT-licensed Human Detectors research dataset, using a released `gpt-4o` sample labeled `AI-generated` and a HumanizerOS-authored rewrite.
- Expanded `EN-LANG-001` with inflated-significance patterns surfaced by the real-world sample and its human annotations, with clean counterexamples in the eval suite.
- Extended Fact Guard to preserve direct quotations while allowing straight/curly quote typography changes.
- Reduced proper-name false positives from sentence scaffolding such as `As Dr.`.

### Planned

- Expressive RU foundation for opt-in detection, preservation, normalization, and censorship.
- Optional LLM adapters with provider-neutral interfaces and local Fact Guard verification.
- Author voice matching with explicit sample consent.
- HumanizerOS Studio and plugin packages for editors and content systems.

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
