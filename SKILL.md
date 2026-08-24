---
name: humanizer-os
description: Rewrite English AI-assisted prose so it reads naturally without changing facts, code, links, quotations, or the writer's voice. Use for humanizing, de-templating, rewriting, or reviewing prose. English is the default; switch to Russian for clearly Russian source text or an explicit Russian request.
license: MIT
metadata:
  version: "0.1.0"
---

# HumanizerOS

Make AI-assisted English read like deliberate human prose. Preserve the source meaning, retain useful quirks, and change only the passages that need editorial work.

English is the default. Russian is an optional supported locale.

## Guardrails

- Preserve names, numbers, dates, prices, units, URLs, email addresses, citations, direct quotations, code, deadlines, product terms, and calls to action.
- Never invent personal experience, emotions, sensory detail, mistakes, evidence, sources, customer claims, or product facts.
- Keep genuine limitations, objections, contrasts, attribution, and technical terminology even when their wording resembles a common pattern.
- Leave clean prose alone instead of rewriting it for novelty.
- Adapt the intervention to the genre. Legal, academic, technical, reference, fictional, marketing, and personal prose have different boundaries.
- Treat findings as editorial evidence, not proof of human or model authorship.

## Workflow

1. Identify the requested outcome and genre.
2. Select English unless the source is clearly Russian or the user asks for Russian.
3. Protect facts and non-prose spans before editing.
4. Audit for concrete patterns rather than a vague sense of artificiality.
5. Rewrite semantically where clarity, rhythm, or specificity improves.
6. Review the revision for residual formulaic language and accidental over-editing.
7. Verify protected values before returning the result.

Use the CLI as a deterministic control layer when it is installed:

```bash
humanizer-os audit <path> --lang en --genre <genre> --format json
humanizer-os verify <original> <revised>
```

Russian mode changes the locale rather than translating English rules word for word:

```bash
humanizer-os audit <path> --lang ru --genre <genre> --format json
```

A failed Fact Guard check means the original protected value should be restored unless the user explicitly requested that factual change.

## English review map

### Assistant residue

Look for wrappers such as `Here is the revised version`, internal citation identifiers, unresolved placeholders, fake links, and closing offers that belong to the chat rather than the document.

### Claims and attribution

Question importance language that exceeds the evidence. Replace vague phrases such as `experts believe` with a named source, a precise limitation, or no attribution when none exists.

Do not weaken a supported claim merely because it sounds confident. The problem is unsupported emphasis, not confidence itself.

### Language

Common review targets include:

- ceremonial alternatives to `is` and `has`;
- verbose connectives such as `in order to`;
- stacked hedging and meta-instructions;
- generic product adjectives;
- filler that announces the point before making it.

### Rhetoric

Check generic openings, stock `not just X but Y` contrasts, announced transitions, formulaic conclusions, fake-candid framing, and canned question-answer fragments.

A real contrast or useful transition should stay. Revise the formula only when it carries emphasis without content.

### Structure and formatting

Review repeated sentence openings, stacks of tiny fragments, mechanically uniform rhythm, transition-heavy paragraphs, title-case headings, bold mini-headings, emoji bullets, and excessive list density.

Structural findings have lower certainty than assistant artifacts. Use them as prompts for editorial review rather than automatic deletion.

## Rewriting principles

- Lead with the subject, event, decision, or example.
- Prefer concrete verbs and observable consequences.
- Vary sentence length for meaning, not randomness.
- Merge fragments that imitate punchiness without adding precision.
- Remove generic praise unless the source supports it.
- Preserve deliberate humor, bluntness, uncertainty, and technical register.
- Avoid invented anecdotes or artificial mistakes.

## Voice matching

Use author samples only when the user provides them. Match observable traits such as sentence length, paragraph rhythm, punctuation, directness, use of lists, and degree of formality.

Do not infer identity, biography, personality, demographics, or private experience from writing samples.

## Output modes

**Audit** reports findings without changing the source.

**Rewrite** returns improved prose while preserving protected values.

**Safe fix** applies only unambiguous local replacements.

**Voice-aware rewrite** follows supplied samples without inventing personal detail.

For a requested rewrite, return the revised text first. Add a compact change summary only when it helps the user understand a meaningful editorial decision or a Fact Guard conflict.
