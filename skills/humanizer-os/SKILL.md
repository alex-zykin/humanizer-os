---
name: humanizer-os
description: Rewrite English or Russian AI-assisted prose so it reads naturally without changing facts, code, links, or the writer's voice. Use when the user asks to humanize, de-template, rewrite, or review prose; audit first and use HumanizerOS Fact Guard when available.
---

# HumanizerOS: make AI-assisted writing sound human

Rewrite English or Russian prose so it reads like a person wrote it, not like a generic chatbot. Preserve what the text says, keep the writer's deliberate voice, and change only what needs work.

## Non-negotiable rules

- Never claim that a finding proves human or AI authorship.
- Preserve names, numbers, dates, prices, units, URLs, email addresses, citations, quotes, code, deadlines, and calls to action.
- Do not invent personal experience, emotions, mistakes, sensory detail, evidence, or sources.
- Do not rewrite clean text merely to make it different.
- Treat legal, academic, technical, fictional, and quoted language as separate genres with wider exceptions.

## Preferred workflow

1. Determine language and genre.
2. If the `humanizer-os` CLI is available, run an audit first:

```bash
humanizer-os audit <path> --lang auto --genre <genre> --format json
```

3. Explain the highest-impact findings with exact excerpts.
4. Rewrite only when the user requested a rewrite. Fix the reported problem, not every stylistic difference.
5. Run Fact Guard or compare protected facts manually:

```bash
humanizer-os verify <original> <revised>
```

6. If verification fails, restore the original fact and call out the conflict.

## Without the CLI

Audit in three passes:

- artifacts: assistant wrappers, internal citation IDs, placeholders, broken markup;
- language and rhetoric: generic openings, vague attribution, bureaucratic phrasing, canned contrasts, over-announced transitions;
- structure: repeated openings, stacks of fragments, uniform paragraph rhythm, excessive signposting.

Label structural findings as contextual rather than definitive.

## Output modes

- **Audit**: findings only; do not change the text.
- **Safe fix**: apply only unambiguous local replacements.
- **Rewrite**: diagnose first, then revise while preserving protected facts.
- **Voice-aware rewrite**: use supplied writing samples for observable rhythm and punctuation; never infer biography or identity.
