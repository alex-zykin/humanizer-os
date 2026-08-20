# Rule provenance

## Principle

HumanizerOS uses public research and open projects to discover ideas, then writes its own rule text, examples, detectors, thresholds, tests, and code. A source supports consideration of a pattern; it does not prove that every occurrence is wrong.

## Source classes

### Primary research

- StoryScope: Jenna Russell, Rishanth Rajendhran, Chau Minh Pham, Mohit Iyyer, and John Wieting, 2026, arXiv:2604.03136.
- Human Detectors: Jenna Russell, Marzena Karpinska, and Mohit Iyyer, 2025, arXiv:2501.15654; code/data at `jenna-russell/human_detectors`, MIT at time of review.

StoryScope informs the separation between surface and discourse signals. Its long-fiction findings are not applied as universal short-form rules.

Human Detectors provides labeled nonfiction samples plus human annotations. HumanizerOS uses one released machine-generated sample as a real-world demo and as evidence for refining an existing English significance rule. The paired human reference article is not copied into this repository.

### Open catalogs and implementations

- `blader/humanizer`, MIT;
- `smixs/humanizer-ru`, MIT;
- `gc-tilda/pishi-chelovechno`, MIT;
- `ilyautov/humanizer-ru`, MIT;
- `Vladimir-Human/humanizer-ru`, MIT;
- Wikipedia's English and Russian AI-writing signal pages, used as research pointers.

When code or substantial expression is copied from an MIT project, its notice must appear in `THIRD_PARTY_NOTICES.md`. The initial implementation re-authors rule descriptions, examples, detectors, and tests instead of copying substantial source files.

## Real-world demo policy

A research sample may be included only when its publication terms permit redistribution and its provenance is explicit. For `examples/real-world-ai-*`:

- the source is a machine-generated record from the Human Detectors repository;
- its ground-truth label and generation-model metadata come from the released dataset;
- the rewrite is authored for HumanizerOS;
- the paired human-written reference article is not reproduced;
- direct quotations and claims are preserved for editorial comparison, not endorsed as factually true;
- Fact Guard checks consistency only.

## Unlicensed sources

`nickname76/russian-swears` contains useful research navigation but has no license and cites third-party websites. HumanizerOS does not vendor its definitions, examples, or list. Expressive RU will use independently authored entries, licensed linguistic references, explicit permissions, and per-entry provenance.

## Rule record

Each rule includes `sources`. Future external packs should add:

```json
{
  "provenance": {
    "kind": "independently-authored",
    "sources": ["..."],
    "license_notes": "No copied expression"
  }
}
```

## Contributions

A rule proposal must provide:

- an observable pattern;
- a positive example;
- a legitimate or adversarial example;
- genre and quote boundaries;
- evidence links;
- license notes;
- a false-positive explanation.

Generated text can be used to create a minimal fixture when the contributor has the right to publish it. Do not submit private prompts, customer data, or copyrighted corpus passages.
