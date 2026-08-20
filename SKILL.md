---
name: humanizer-os
description: Rewrite English AI-assisted prose so it reads naturally without changing facts, code, links, or the writer's voice. Use when the user asks to humanize, de-template, rewrite, or review prose. English is the default; switch to the Russian pack when the source is Russian or the user explicitly requests Russian.
license: MIT
metadata:
  version: "0.1.0"
---

# HumanizerOS: make AI-assisted writing sound human

HumanizerOS is English-first. Rewrite English prose so it reads like a person wrote it, not like a generic chatbot. Preserve what the text says, keep the writer's deliberate voice, and change only what needs work.

Russian is an optional supported locale. Switch to Russian only when the user asks for Russian or the source text is clearly Russian.

## Non-negotiable rules

- Never claim that a finding proves human or AI authorship.
- Preserve names, numbers, dates, prices, units, URLs, email addresses, citations, quotes, code, deadlines, and calls to action.
- Do not invent personal experience, emotions, mistakes, sensory detail, evidence, or sources.
- Do not rewrite clean text merely to make it different.
- Treat legal, academic, technical, fictional, and quoted language as separate genres with wider exceptions.

## Preferred workflow

1. Use English by default. Switch to Russian when the user selects Russian or the source is clearly Russian.
2. Determine the genre.
3. If the `humanizer-os` CLI is available, audit before rewriting:

```bash
humanizer-os audit <path> --lang en --genre <genre> --format json
```

For Russian:

```bash
humanizer-os audit <path> --lang ru --genre <genre> --format json
```

4. Explain the highest-impact findings with exact excerpts when that helps the user.
5. Rewrite only when the user requested a rewrite. Fix the reported problem, not every stylistic difference.
6. Run Fact Guard or compare protected facts manually:

```bash
humanizer-os verify <original> <revised>
```

7. If verification fails, restore the original fact and call out the conflict.

## Without the CLI

Audit in three passes:

- artifacts: assistant wrappers, internal citation IDs, placeholders, broken markup;
- language and rhetoric: generic openings, vague attribution, inflated claims, canned contrasts, filler, and over-announced transitions;
- structure: repeated openings, stacks of fragments, uniform paragraph rhythm, and excessive signposting.

When working in Russian, use Russian-specific constructions and grammar rather than translating English rules word-for-word.

Label structural findings as contextual rather than definitive.

## Output modes

- **Audit**: findings only; do not change the text.
- **Safe fix**: apply only unambiguous local replacements.
- **Rewrite**: diagnose first, then revise while preserving protected facts.
- **Voice-aware rewrite**: use supplied writing samples for observable rhythm and punctuation; never infer biography or identity.
