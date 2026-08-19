# HumanizerOS platform

HumanizerOS is an open platform for humanizing text across languages, genres, author voices, agents, and products. Version 0.1 ships the deterministic kernel: analysis, safe local fixes, fact verification, stable JSON/SARIF contracts, English and Russian language packs, CLI/API integration, and Agent Skills.

The platform grows through modules. The core remains a usable product rather than a thin launcher for remote models.

## Product layers

| Layer | Responsibility | Network |
|---|---|---|
| **HumanizerOS Core** | analysis, protected spans, metrics, safe replacements, Fact Guard, contracts | never |
| **HumanizerOS RU / EN** | language-native rules, examples, boundaries, evals | never |
| **HumanizerOS Skills** | Agent Skills that call the same core contracts | never by default |
| **HumanizerOS Voice** | opt-in author samples and measurable voice constraints | local by default |
| **Expressive RU** | opt-in Russian expression, including contextual profanity controls | local catalog; generation optional |
| **HumanizerOS Providers** | semantic rewrite adapters for hosted or local models | explicit |
| **HumanizerOS Studio** | visual review, diff, profiles, policy, and team workflows | deployment-dependent |
| **Integrations** | editor plugins, CI, Content OS, batch pipelines | deployment-dependent |

## Shared contracts

Every module must respect:

- stable rule IDs and source positions;
- protected facts and spans;
- explicit locale and genre;
- versioned JSON payloads;
- provenance and license metadata;
- visible network boundaries;
- deterministic mode for CI;
- no claims of authorship certainty.

A provider may propose a semantic rewrite, but Core verifies it. A voice profile may constrain tone, but it may not invent personal history. An expression module may preserve or normalize profanity, but adding it requires an explicit request.

## Language packs

A language pack is a product, not a translation file. It contains:

- curated rules;
- detector parameters;
- genre exclusions;
- examples;
- safe replacement policy;
- eval fixtures;
- provenance.

Shared detectors reduce implementation duplication. Independent catalogs prevent English syntax from being projected onto Russian.

## Expressive RU

Expressive RU is planned as an installable, disabled-by-default module. Its first release covers:

- detection and preservation;
- functional classes such as frustration, emphasis, humor, admiration, and self-irony;
- intensity and targeting metadata;
- normalization and platform masking;
- restrictions for personal attacks and protected-group slurs;
- independently authored, provenance-tracked data.

The unlicensed `russian-swears` repository is research navigation, not vendored data. A generative `add` mode belongs behind an explicit provider and deterministic post-checks.

## Provider-neutral rewriting

A future adapter receives a structured request rather than a monolithic prompt:

```json
{
  "text": "...",
  "language": "ru",
  "genre": "social",
  "findings": [],
  "protected_facts": [],
  "voice_profile": null,
  "expression_policy": {"mode": "preserve"}
}
```

The response passes through Fact Guard, policy checks, and a second audit. The original is returned if the contract fails.

## HumanizerOS Studio

Studio is the planned visual surface for:

- side-by-side source, revised text, and diff;
- per-finding accept/reject;
- language and genre profiles;
- rule explanations and provenance;
- Fact Guard changes;
- author voice samples;
- provider and privacy controls;
- project-level policy baselines.

The web product should consume the same schemas as the CLI and Python package.

## Integration with Creator Content OS

HumanizerOS remains a separate public project and integrates with Creator Content OS through JSON/API contracts. This preserves independent community development while giving creators a first-class editor inside their content workflow.

## Stability path

`0.x` may refine CLI names and schemas with changelog entries. `1.0` requires:

- published compatibility policy;
- measured false-positive budgets by language and genre;
- blinded reader evaluation for semantic rewrites;
- signed release artifacts;
- configuration and baseline support;
- documented extension API;
- complete privacy controls for provider adapters.
