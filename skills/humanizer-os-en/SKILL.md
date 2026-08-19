---
name: humanizer-os-en
description: Audits and safely edits English prose for formulaic language, chatbot artifacts, unsupported attribution, templated rhetoric, and fact drift.
---

# HumanizerOS English

Use for English prose when the user asks to humanize, edit, de-template, audit, or remove formulaic AI-style writing.

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
