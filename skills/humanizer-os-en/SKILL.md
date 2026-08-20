---
name: humanizer-os-en
description: Rewrite AI-assisted English prose so it reads naturally without changing facts, code, links, or the writer's voice. Use when the user asks to humanize, de-template, rewrite, or review English text for chatbot artifacts and formulaic patterns.
license: MIT
metadata:
  version: "0.1.0"
---

# HumanizerOS English

Rewrite English prose so it reads like a person wrote it, not like a generic chatbot. Preserve what the text says and keep deliberate voice and genre choices.

## Guardrails

- A style pattern is not proof of authorship.
- Keep every name, number, date, quote, citation, URL, price, deadline, code fragment, and concrete claim.
- Never add anecdotes or emotions that the author did not provide.
- Respect deliberate voice and genre. Contracts, research, documentation, and fiction have different constraints.

## Workflow

Run the local analyzer when available:

```bash
humanizer-os audit <path> --lang en --genre <genre>
humanizer-os fix <path> --lang en --genre <genre> --diff
humanizer-os verify <original> <revised>
```

Review high-confidence artifacts first, then language and rhetoric, then low-confidence structural signals.

Common review targets include assistant wrappers, internal citations, vague experts, inflated importance, “not just X but Y,” filler connectives, announced transitions, formulaic conclusions, title-case headings, bold mini-heading lists, and mechanically even rhythm.

Do not replace a valid contrast, technical term, quotation, or house style merely because it matches a surface pattern.
