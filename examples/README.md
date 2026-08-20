# Reproducible product-launch demo

This example is used by the main README to show the difference between rewriting alone and a HumanizerOS workflow.

## Source

[`product-launch-before.md`](product-launch-before.md) intentionally contains several common AI-assisted writing patterns while also carrying concrete facts that must survive the edit.

Run:

```bash
humanizer-os audit examples/product-launch-before.md --lang en --genre landing
```

The source contains **10 findings across 8 rules**:

- `EN-OPEN-001` — generic scene-setting opening;
- `EN-RHET-001` — `not just X, but Y` contrast;
- `EN-LANG-001` — two inflated-importance matches;
- `EN-LANG-005` — two meta/hedging matches;
- `EN-LANG-006` — marketing adjective stack;
- `EN-LANG-002` — vague attribution;
- `EN-RHET-003` — formulaic conclusion;
- `EN-CONTENT-001` — generic positive ending.

## Revised copy

[`product-launch-after.md`](product-launch-after.md) keeps the concrete launch information while removing the formulaic framing.

Verify the protected surface facts:

```bash
humanizer-os verify \
  examples/product-launch-before.md \
  examples/product-launch-after.md
```

Expected result:

```text
OK  Protected facts match (6 checked).
```

Those six protected facts are two occurrences of `Acme Cloud Pro`, the date `September 15, 2026`, the price `$49`, the number `25`, and the URL `https://example.com/pro`.

The revised text is a semantic example for an agent workflow. HumanizerOS's deterministic `fix` command does not attempt to rewrite the whole passage; it only applies replacements that are explicitly marked safe.
