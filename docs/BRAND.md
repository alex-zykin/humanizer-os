# HumanizerOS brand guide

HumanizerOS is marketed to an English-speaking audience first. English is the default language across the repository, social copy, screenshots, examples, Agent Skill descriptions, and future product surfaces.

Russian is a supported locale and localized experience, not a co-primary marketing language. Russian copy belongs in `README.ru.md`, `skills/humanizer-os-ru/`, locale-specific examples, and translated product views.

## Naming

Use `HumanizerOS` for the product.

Use `humanizer-os` for the repository, Python distribution, CLI, and canonical Agent Skill.

Reserve `humanizer_os` for Python imports.

Refer to the optional locale as `Russian support` or `HumanizerOS Russian`. Avoid presenting `RU / EN` as two equal top-level products in primary marketing copy.

## Positioning

Headline:

**Humanize the writing. Verify the facts.**

Supporting line:

**Make AI-assisted English sound natural with explainable edits and Fact Guard.**

Locale note:

**Russian available when you need it.**

## Proof hierarchy

Public product surfaces should show value in this order:

1. a clear before-and-after result;
2. the findings that informed the rewrite;
3. Fact Guard verification;
4. installation for agents;
5. the deterministic runtime and integrations;
6. optional Russian support;
7. deeper architecture and methodology.

Do not lead with rule counts, `multilingual platform`, or internal module names before the user has seen the outcome.

## Visual assets

The repository includes:

- `assets/hero.svg` for the README header;
- `assets/verified-rewrite.svg` for the primary proof-of-value demo;
- `assets/terminal-demo.svg` for the engine walkthrough;
- `assets/social-preview.png` for GitHub social sharing when that asset is available.

Keep the main visual system in English. Localized Russian pages may use Russian copy and examples.

## Tone

Product writing should be direct, evidence-led, and calm. Show what changed instead of declaring that the product is revolutionary, magical, undetectable, or universally human.

Recommended vocabulary:

- humanize;
- explainable editing;
- Fact Guard;
- protected values;
- language-native rules;
- agent workflow;
- local-first core.

Avoid claims about bypassing detectors or proving authorship. HumanizerOS improves prose and verifies preserved values; it does not certify who wrote a document.

## Demo policy

A public demo should include source provenance, a complete or reproducible input, the revision, current findings, and a Fact Guard result. Synthetic examples must be labeled as synthetic. Real-world samples require compatible publication terms and explicit source notes.

Marketing numbers belong in regression tests whenever possible. A README claim should fail CI if the underlying engine behavior changes.
