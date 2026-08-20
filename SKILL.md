---
name: humanizer-os
description: Rewrite English AI-assisted prose so it reads naturally without changing facts, code, links, or the writer's voice. Use when the user asks to humanize, de-template, rewrite, or review prose. English is the default; switch to Russian when the source is Russian or the user explicitly requests Russian.
license: MIT
metadata:
  version: "0.1.0"
---

# HumanizerOS: humanize the writing, verify the facts

Rewrite AI-assisted English so it reads like deliberate human prose rather than a generic chatbot answer. Preserve what the text says, keep the writer's useful quirks, and change only what needs work.

English is the default. Russian is an optional supported locale.

## Non-negotiable rules

- Preserve names, numbers, dates, prices, units, URLs, email addresses, citations, quotes, code, deadlines, product terms, and calls to action.
- Do not invent personal experience, emotions, sensory details, mistakes, evidence, sources, customer claims, or product facts.
- Do not remove a real limitation, objection, contrast, attribution, or technical term simply because it resembles a common AI-writing pattern.
- Do not rewrite clean prose merely to make it different.
- Respect genre. Legal, academic, technical, reference, fictional, marketing, and personal prose need different levels of intervention.
- Never claim that a pattern proves human or AI authorship.

## Preferred workflow

1. Determine the genre and the user's requested outcome.
2. Use English unless the source is clearly Russian or the user explicitly selects Russian.
3. Protect facts and non-prose spans before editing.
4. Audit the draft for concrete patterns.
5. Rewrite semantically. Paragraph boundaries and sentence order may change when clarity improves.
6. Re-read the revision for remaining formulaic patterns.
7. Verify protected facts before returning the result.

When the HumanizerOS CLI is available, use it as the deterministic control layer:

```bash
humanizer-os audit <path> --lang en --genre <genre> --format json
humanizer-os verify <original> <revised>
```

For Russian, switch the locale:

```bash
humanizer-os audit <path> --lang ru --genre <genre> --format json
```

If Fact Guard reports a difference, restore the original protected value unless the user explicitly requested that factual change.

## English review map

When the CLI is unavailable, scan the text with this checklist before rewriting.

### Artifacts

Remove assistant residue that does not belong in the document:

- chatbot prefaces and sign-offs;
- internal citation markers;
- unresolved placeholders;
- excessive agreement or praise before the answer.

### Claims and content

Review:

- vague attribution to unnamed experts, studies, researchers, or industry leaders;
- inflated importance that is not supported by an observable consequence;
- generic positive endings;
- abstract deeper-meaning statements that repeat the previous point;
- objections or alternatives that the reader never raised.

Never invent a source to repair vague attribution. Narrow or remove the unsupported claim when no source exists.

### Language

Look for:

- ceremonial alternatives to plain `is`, `has`, or a concrete action verb;
- long connectives that can be shortened safely;
- stacked hedging or meta-instructions about what the reader should notice;
- promotional adjective stacks that do not describe measurable behavior;
- stock importance language that announces significance instead of showing it.

### Rhetoric

Review:

- generic scene-setting openings;
- canned contrast structures;
- sentences that announce the next section instead of starting it;
- labeled conclusions that repeat the point;
- fake-candid framing;
- tiny question-and-answer pairs used only for conversational rhythm.

A real contrast or real question can stay. Fix the formula, not the existence of contrast or dialogue.

### Formatting

Check whether the text overuses:

- bold emphasis;
- bold mini-headings inside lists;
- Title Case headings;
- decorative emoji bullets;
- lists where prose or a table would show relationships better;
- em dashes at an unusually high rate.

Do not enforce a house style the writer did not ask for. If a supplied writing sample uses these features deliberately, match the sample.

### Structure

For longer prose, review:

- stacks of tiny fragments;
- repeated sentence openings;
- nearly identical paragraph sizes;
- unusually even sentence rhythm;
- explicit transition phrases at the start of most paragraphs.

Treat structural signals as contextual. They are weaker evidence than obvious artifacts or unsupported claims.

## Rewrite policy

A strong rewrite should keep the information while changing the delivery where needed.

Prefer:

- concrete subjects and verbs;
- specific claims over importance language;
- varied sentence length driven by meaning;
- paragraph sizes driven by the amount of information;
- direct transitions when the relationship is already obvious;
- useful uncertainty instead of stacked qualifiers;
- the writer's real humor, preferences, mixed feelings, and deliberate quirks when they already exist.

Avoid adding artificial imperfections just to make the text appear human.

## Match the writer's voice

If the user provides their own writing sample, analyze observable features before rewriting:

- sentence and paragraph length;
- vocabulary and formality;
- punctuation habits;
- use of contractions, asides, questions, lists, and headings;
- repeated phrases and transitions;
- amount of first- or second-person language.

Use the sample as a constraint on style. Do not infer biography, identity, demographics, personality, or experiences that are not present in the sample.

## Russian switch

When the source is Russian or the user asks for Russian, switch language logic rather than translating the English checklist word-for-word.

Pay particular attention to Russian-specific bureaucracy, nominalization, heavy copula constructions, translationese, impersonal passive phrasing, modal hedging, canned therapeutic tone, generic openings, and formulaic conclusions. Preserve Russian punctuation and deliberate colloquial voice when appropriate to the genre.

If the dedicated `humanizer-os-ru` skill is installed, prefer it for Russian-only workflows.

## Return modes

Follow the user's request:

- **Rewrite** — return the revised text. Add a short note only when a fact conflict or meaningful ambiguity needs attention.
- **Audit** — return findings with excerpts and suggestions; do not rewrite.
- **Safe fix** — apply only unambiguous local replacements.
- **Voice-aware rewrite** — match a supplied author sample while preserving facts.

When the user asks for a normal humanization, do the audit internally, rewrite the prose, verify protected facts, and return the clean final version without making the user read the whole checklist.
