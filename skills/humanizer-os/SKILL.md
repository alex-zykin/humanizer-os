---
name: humanizer-os
description: Audits and safely edits English or Russian prose for formulaic writing, assistant artifacts, weak rhetoric, and fact drift. Use when the user asks to humanize, de-template, audit, or make prose sound less formulaic while preserving meaning and facts.
---

# HumanizerOS

Use this skill for English or Russian prose. Detect the language first unless the user specifies it.

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
